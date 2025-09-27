(* nanoPB Runtime Library for B&R Automation Studio *)
(* nanoPB main encode/decode functions *)
(* Ported from nanoPB C library to B&R IEC 61131-3 ST *)

FUNCTION pb_st_encode
	
	iter_ref ACCESS ADR(iter);
	
	(* Initialize field iterator *)
	IF NOT pb_st_field_iter_begin(iter_ref, fields, src_struct) THEN
		pb_st_encode := TRUE; (* Empty message is valid *)
		RETURN;
	END_IF;
	
	(* Encode all fields *)
	REPEAT
		IF NOT pb_st_encode_field(stream, iter_ref) THEN
			pb_st_encode := FALSE;
			RETURN;
		END_IF;
	UNTIL NOT pb_st_field_iter_next(iter_ref) END_REPEAT;
	
	pb_st_encode := TRUE;
	
END_FUNCTION

FUNCTION pb_st_decode
	
	iter_ref ACCESS ADR(iter);
	
	(* Initialize message with default values *)
	pb_st_init_default_values(fields, dest_struct);
	
	(* Decode fields until end of stream *)
	WHILE stream.bytes_left > 0 DO
		(* Read field tag and wire type *)
		IF NOT pb_st_decode_varint(stream, ADR(tag)) THEN
			pb_st_decode := FALSE;
			RETURN;
		END_IF;
		
		(* Extract wire type (3 lowest bits) and tag (remaining bits) *)
		wire_type := UDINT_TO_USINT(tag AND 16#07);
		tag_value := UDINT_TO_UINT(SHR(tag, 3));
		
		(* Find field descriptor *)
		field_found := pb_st_field_iter_begin(iter_ref, fields, dest_struct);
		IF field_found THEN
			field_found := pb_st_field_iter_find(iter_ref, tag_value);
		END_IF;
		
		IF field_found THEN
			(* Decode known field *)
			IF NOT pb_st_decode_field(stream, iter_ref, wire_type) THEN
				pb_st_decode := FALSE;
				RETURN;
			END_IF;
		ELSE
			(* Skip unknown field *)
			IF NOT pb_st_skip_field(stream, wire_type) THEN
				pb_st_decode := FALSE;
				RETURN;
			END_IF;
		END_IF;
	END_WHILE;
	
	pb_st_decode := TRUE;
	
END_FUNCTION

FUNCTION pb_st_encode_field
	
	field_type := field.type AND PB_LTYPE_MASK;
	
	(* Check if field has a value (for optional fields) *)
	has_value := TRUE;
	IF (field.type AND PB_HTYPE_MASK) = PB_HTYPE_OPTIONAL THEN
		IF field.pSize <> 0 THEN
			bool_ptr ACCESS field.pSize;
			has_value := bool_ptr;
		END_IF;
	END_IF;
	
	IF NOT has_value THEN
		pb_st_encode_field := TRUE; (* Skip optional field without value *)
		RETURN;
	END_IF;
	
	(* Encode field tag and wire type *)
	IF NOT pb_st_encode_tag_for_field(stream, field) THEN
		pb_st_encode_field := FALSE;
		RETURN;
	END_IF;
	
	(* Encode field value based on type *)
	CASE field_type OF
		PB_LTYPE_BOOL:
			bool_ptr ACCESS field.pData;
			IF bool_ptr THEN
				pb_st_encode_field := pb_st_encode_varint(stream, 1);
			ELSE
				pb_st_encode_field := pb_st_encode_varint(stream, 0);
			END_IF;
			
		PB_LTYPE_VARINT, PB_LTYPE_UVARINT:
			uint_ptr ACCESS field.pData;
			pb_st_encode_field := pb_st_encode_varint(stream, uint_ptr);
			
		PB_LTYPE_SVARINT:
			int_ptr ACCESS field.pData;
			pb_st_encode_field := pb_st_encode_svarint(stream, int_ptr);
			
		PB_LTYPE_FIXED32:
			uint_ptr ACCESS field.pData;
			pb_st_encode_field := pb_st_encode_fixed32(stream, uint_ptr);

		PB_LTYPE_FIXED64:	
			val_64 ACCESS field.pData;
			pb_st_encode_field := pb_st_encode_fixed64(stream, val_64);
			
		PB_LTYPE_STRING:
			string_ptr ACCESS field.pData;
			pb_st_encode_field := pb_st_encode_string(stream, ADR(string_ptr));
			
	ELSE
		stream.errmsg := PB_ERR_INVALID_FIELD;
		pb_st_encode_field := FALSE;
	END_CASE;
	
END_FUNCTION

FUNCTION pb_st_decode_field
	
	field_type := field.type AND PB_LTYPE_MASK;
	
	(* Determine expected wire type *)
	CASE field_type OF
		PB_LTYPE_BOOL, PB_LTYPE_VARINT, PB_LTYPE_UVARINT, PB_LTYPE_SVARINT:
			expected_wire_type := PB_WT_VARINT;
		PB_LTYPE_FIXED32:
			expected_wire_type := PB_WT_32BIT;
		PB_LTYPE_FIXED64:
			expected_wire_type := PB_WT_64BIT;
		PB_LTYPE_STRING, PB_LTYPE_BYTES:
			expected_wire_type := PB_WT_STRING;
	ELSE
		stream.errmsg := PB_ERR_INVALID_FIELD;
		pb_st_decode_field := FALSE;
		RETURN;
	END_CASE;
	
	(* Check wire type matches *)
	IF wire_type <> expected_wire_type THEN
		stream.errmsg := PB_ERR_INVALID_WIRE_TYPE;
		pb_st_decode_field := FALSE;
		RETURN;
	END_IF;
	
	(* Decode field value based on type *)
	CASE field_type OF
		PB_LTYPE_BOOL:
			IF pb_st_decode_varint(stream, ADR(temp_uint)) THEN
				bool_ptr ACCESS field.pData;
				bool_ptr := (temp_uint <> 0);
				pb_st_decode_field := TRUE;
			ELSE
				pb_st_decode_field := FALSE;
			END_IF;
			
		PB_LTYPE_VARINT, PB_LTYPE_UVARINT:
			pb_st_decode_field := pb_st_decode_varint(stream, field.pData);
			
		PB_LTYPE_SVARINT:
			pb_st_decode_field := pb_st_decode_svarint(stream, field.pData);
			
		PB_LTYPE_FIXED32:
			pb_st_decode_field := pb_st_decode_fixed32(stream, field.pData);
			
		PB_LTYPE_FIXED64:
			pb_st_decode_field := pb_st_decode_fixed64(stream, field.pData);

		PB_LTYPE_STRING:
			pb_st_decode_field := pb_st_decode_string(stream, field.pData, 255);
			
	ELSE
		stream.errmsg := PB_ERR_INVALID_FIELD;
		pb_st_decode_field := FALSE;
	END_CASE;
	
	(* Set has_field flag for optional fields *)
	IF pb_st_decode_field AND ((field.type AND PB_HTYPE_MASK) = PB_HTYPE_OPTIONAL) THEN
		IF field.pSize <> 0 THEN
			bool_ptr ACCESS field.pSize;
			bool_ptr := TRUE;
		END_IF;
	END_IF;
	
END_FUNCTION

FUNCTION pb_st_init_default_values
	
	(* For now, just zero out the entire structure *)
	(* In a full implementation, this would set proper default values *)
//	brsmemset(dest_struct, 0, 1024); (* Assume max 1KB message size *)
	pb_st_init_default_values := TRUE;
	
END_FUNCTION

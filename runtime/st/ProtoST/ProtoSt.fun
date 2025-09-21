(* nanoPB library functions ported to B&R IEC 61131-3 ST *)
(* ===== STREAM FUNCTIONS ===== *)

FUNCTION pb_st_istream_from_buffer : UDINT (*Create input stream from buffer - returns address*) (*$GROUP=nanoPB,$CAT=Stream,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Stream to initialize *)
		buf : REFERENCE TO pb_byte_t; (* Buffer containing data *)
		bufsize : pb_size_t; (* Size of buffer *)
	END_VAR
END_FUNCTION

FUNCTION pb_st_ostream_from_buffer : UDINT (*Create output stream from buffer - returns address*) (*$GROUP=nanoPB,$CAT=Stream,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Stream to initialize *)
		buf : REFERENCE TO pb_byte_t; (* Buffer to write to *)
		bufsize : pb_size_t; (* Size of buffer *)
	END_VAR
END_FUNCTION

FUNCTION pb_st_read : BOOL (*Read data from input stream*) (*$GROUP=nanoPB,$CAT=Stream,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		buf : UDINT; (* Buffer to read into *)
		count : pb_size_t; (* Number of bytes to read *)
	END_VAR
	VAR
		i : pb_size_t;
		src_ptr : REFERENCE TO pb_byte_t;
		dest_ptr : REFERENCE TO pb_byte_t;
	END_VAR
END_FUNCTION

FUNCTION pb_st_write : BOOL (*Write data to output stream*) (*$GROUP=nanoPB,$CAT=Stream,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Output stream *)
		buf : UDINT; (* Buffer to write from *)
		count : pb_size_t; (* Number of bytes to write *)
	END_VAR
	VAR
		i : pb_size_t;
		src_ptr : REFERENCE TO pb_byte_t;
		dest_ptr : REFERENCE TO pb_byte_t;
	END_VAR
END_FUNCTION
(* ===== VARINT FUNCTIONS ===== *)

FUNCTION pb_st_encode_varint : BOOL (*Encode unsigned varint*) (*$GROUP=nanoPB,$CAT=Varint,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Output stream *)
		value : UDINT; (* Value to encode *)
	END_VAR
	VAR
		buffer : ARRAY[0..9] OF pb_byte_t; (* Max 10 bytes for 64-bit varint *)
		i : USINT;
		bytes_written : USINT;
	END_VAR
END_FUNCTION

FUNCTION pb_st_decode_varint : BOOL (*Decode unsigned varint*) (*$GROUP=nanoPB,$CAT=Varint,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		dest : REFERENCE TO UDINT; (* Destination for decoded value *)
	END_VAR
	VAR
		byte_val : pb_byte_t;
		bitpos : USINT;
		result : UDINT;
	END_VAR
END_FUNCTION

FUNCTION pb_st_encode_svarint : BOOL (*Encode signed varint (zigzag)*) (*$GROUP=nanoPB,$CAT=Varint,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Output stream *)
		value : DINT; (* Signed value to encode *)
	END_VAR
	VAR
		encoded : UDINT;
	END_VAR
END_FUNCTION

FUNCTION pb_st_decode_svarint : BOOL (*Decode signed varint (zigzag)*) (*$GROUP=nanoPB,$CAT=Varint,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		dest : REFERENCE TO DINT; (* Destination for decoded value *)
	END_VAR
	VAR
		encoded : UDINT;
	END_VAR
END_FUNCTION
(* ===== FIELD ENCODING/DECODING ===== *)

FUNCTION pb_st_encode_tag_for_field : BOOL (*Encode field tag and wire type*) (*$GROUP=nanoPB,$CAT=Field,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Output stream *)
		field : pb_field_iter_struct; (* Field iterator *)
	END_VAR
	VAR
		wire_type : USINT;
		tag_and_type : UDINT;
		length : UDINT;
	END_VAR
END_FUNCTION

FUNCTION pb_st_encode_string : BOOL (*Encode string field*) (*$GROUP=nanoPB,$CAT=Field,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Output stream *)
		s : REFERENCE TO STRING[80]; (* String to encode *)
	END_VAR
	VAR
		str_len : pb_size_t;
	END_VAR
END_FUNCTION

FUNCTION pb_st_decode_string : BOOL (*Decode string field*) (*$GROUP=nanoPB,$CAT=Field,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		dest : REFERENCE TO STRING[80]; (* Destination string *)
		size : pb_size_t; (* Maximum string size *)
	END_VAR
	VAR
		str_len : UDINT;
		temp_str : STRING[255];
	END_VAR
END_FUNCTION

FUNCTION pb_st_encode_fixed32 : BOOL (*Encode 32-bit fixed field*) (*$GROUP=nanoPB,$CAT=Field,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Output stream *)
		value : UDINT; (* Value to encode *)
	END_VAR
	VAR
		bytes : ARRAY[0..3] OF pb_byte_t;
	END_VAR
END_FUNCTION

FUNCTION pb_st_decode_fixed32 : BOOL (*Decode 32-bit fixed field*) (*$GROUP=nanoPB,$CAT=Field,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		dest : REFERENCE TO UDINT; (* Destination for value *)
	END_VAR
	VAR
		bytes : ARRAY[0..3] OF pb_byte_t;
	END_VAR
END_FUNCTION

FUNCTION pb_st_encode_fixed64 : BOOL (*Encode 64-bit fixed field*) (*$GROUP=nanoPB,$CAT=Field,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Output stream *)
		value : pb_uint64_struct; (* Value to encode *)
	END_VAR
	VAR
		bytes : ARRAY[0..7] OF pb_byte_t;
		i : USINT;
	END_VAR
END_FUNCTION

FUNCTION pb_st_decode_fixed64 : BOOL (*Decode 64-bit fixed field*) (*$GROUP=nanoPB,$CAT=Field,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		dest : REFERENCE TO pb_uint64_struct; (* Destination for value *)
	END_VAR
	VAR
		bytes : ARRAY[0..7] OF pb_byte_t;
		i : USINT;
	END_VAR
END_FUNCTION
(* ===== FIELD ITERATOR FUNCTIONS ===== *)

FUNCTION pb_st_field_iter_begin : BOOL (*Initialize field iterator*) (*$GROUP=nanoPB,$CAT=Iterator,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		iter : pb_field_iter_struct; (* Iterator to initialize *)
		descriptor : pb_msgdesc_struct; (* Message descriptor *)
		message : UDINT; (* Message structure *)
	END_VAR
END_FUNCTION

FUNCTION pb_st_field_iter_next : BOOL (*Move to next field*) (*$GROUP=nanoPB,$CAT=Iterator,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		iter : pb_field_iter_struct; (* Field iterator *)
	END_VAR
	VAR
		desc_ref : REFERENCE TO pb_msgdesc_struct;
		field_info_ptr : REFERENCE TO ARRAY[0..0] OF UDINT;
		prev_descriptor : UDINT;
		descriptor_len : UDINT;
		prev_type : USINT;
	END_VAR
END_FUNCTION

FUNCTION pb_st_field_iter_find : BOOL (*Find field by tag*) (*$GROUP=nanoPB,$CAT=Iterator,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		iter : pb_field_iter_struct; (* Field iterator *)
		tag : pb_size_t; (* Tag to find *)
	END_VAR
	VAR
		dpb_msgdesc_struct : REFERENCE TO pb_msgdesc_struct;
	END_VAR
END_FUNCTION
(* ===== MAIN ENCODE/DECODE FUNCTIONS ===== *)

FUNCTION pb_st_encode : BOOL (*Encode message to stream*) (*$GROUP=nanoPB,$CAT=Main,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Output stream *)
		fields : pb_msgdesc_struct; (* Message descriptor *)
		src_struct : UDINT; (* Source message structure *)
	END_VAR
	VAR
		iter : pb_field_iter_struct;
		iter_ref : REFERENCE TO pb_field_iter_struct;
	END_VAR
END_FUNCTION

FUNCTION pb_st_decode : BOOL (*Decode message from stream*) (*$GROUP=nanoPB,$CAT=Main,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		fields : pb_msgdesc_struct; (* Message descriptor *)
		dest_struct : UDINT; (* Destination message structure *)
	END_VAR
	VAR
		tag : UDINT;
		wire_type : pb_wire_type_t;
		tag_value : pb_size_t;
		iter : pb_field_iter_struct;
		iter_ref : REFERENCE TO pb_field_iter_struct;
		field_found : BOOL;
	END_VAR
END_FUNCTION
(* ===== UTILITY FUNCTIONS ===== *)

FUNCTION pb_st_skip_field : BOOL (*Skip unknown field based on wire type*) (*$GROUP=nanoPB,$CAT=Utility,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		wire_type : pb_wire_type_t; (* Wire type of field to skip *)
	END_VAR
	VAR
		length : UDINT;
		dummy_value : UDINT;
		dummy_value64 : pb_uint64_struct;
	END_VAR
END_FUNCTION

FUNCTION pb_st_make_string_substream : BOOL (*Create substream for string/bytes*) (*$GROUP=nanoPB,$CAT=Utility,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		substream : pb_istream_struct; (* Substream to create *)
	END_VAR
	VAR
		length : UDINT;
	END_VAR
END_FUNCTION

FUNCTION pb_st_close_string_substream : BOOL (*Close string/bytes substream*) (*$GROUP=nanoPB,$CAT=Utility,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Original stream *)
		substream : pb_istream_struct; (* Substream to close *)
	END_VAR
END_FUNCTION
(* ===== INTERNAL HELPER FUNCTIONS ===== *)

FUNCTION pb_st_load_descriptor_values : BOOL (*Load field descriptor values*) (*$GROUP=nanoPB,$CAT=Internal,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		iter : pb_field_iter_struct; (* Field iterator *)
	END_VAR
	VAR
		desc_ref : REFERENCE TO pb_msgdesc_struct;
		word0 : UDINT;
		word1 : UDINT;
		word2 : UDINT;
		word3 : UDINT;
		word4 : UDINT;
		data_offset : UDINT;
		size_offset : DINT;
		size_offset_raw : UDINT;
		descriptor_format : UDINT;
		field_info_ptr : REFERENCE TO ARRAY[0..0] OF UDINT;
		ptr_ptr : REFERENCE TO UDINT;
	END_VAR
END_FUNCTION

FUNCTION pb_st_encode_field : BOOL (*Encode single field*) (*$GROUP=nanoPB,$CAT=Internal,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_ostream_struct; (* Output stream *)
		field : pb_field_iter_struct; (* Field iterator *)
	END_VAR
	VAR
		field_type : USINT;
		has_value : BOOL;
		bool_ptr : REFERENCE TO BOOL;
		int_ptr : REFERENCE TO DINT;
		uint_ptr : REFERENCE TO UDINT;
		real_ptr : REFERENCE TO REAL;
		val_64 : REFERENCE TO pb_uint64_struct;
		string_ptr : REFERENCE TO STRING[80];
	END_VAR
END_FUNCTION

FUNCTION pb_st_decode_field : BOOL (*Decode single field*) (*$GROUP=nanoPB,$CAT=Internal,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		stream : pb_istream_struct; (* Input stream *)
		field : pb_field_iter_struct; (* Field iterator *)
		wire_type : pb_wire_type_t; (* Wire type from tag *)
	END_VAR
	VAR
		field_type : USINT;
		expected_wire_type : pb_wire_type_t;
		temp_uint : UDINT;
		bool_ptr : REFERENCE TO BOOL;
	END_VAR
END_FUNCTION

FUNCTION pb_st_init_default_values : BOOL (*Initialize message with defaults*) (*$GROUP=nanoPB,$CAT=Internal,$GROUPICON=User.png,$CATICON=User.png*)
	VAR_INPUT
		fields : pb_msgdesc_struct; (* Message descriptor *)
		dest_struct : REFERENCE TO UDINT; (* Message structure *)
	END_VAR
END_FUNCTION

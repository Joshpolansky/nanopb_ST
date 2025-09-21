(* nanoPB varint encoding/decoding functions *)
(* Ported from nanoPB C library to B&R IEC 61131-3 ST *)

FUNCTION pb_st_encode_varint
	
	(* Encode varint using 7-bit encoding *)
	i := 0;
	
	REPEAT
		buffer[i] := UDINT_TO_USINT(value AND 16#7F); (* Take lower 7 bits *)
		value := SHR(value, 7); (* Shift right by 7 bits *)
		
		IF value <> 0 THEN
			buffer[i] := buffer[i] OR 16#80; (* Set continuation bit *)
		END_IF;
		
		i := i + 1;
	UNTIL value = 0 OR i >= 10 END_REPEAT;
	
	bytes_written := i;
	
	(* Write the encoded bytes to stream *)
	pb_st_encode_varint := pb_st_write(stream, ADR(buffer[0]), bytes_written);
	
END_FUNCTION

FUNCTION pb_st_decode_varint
	
	result := 0;
	bitpos := 0;
	
	(* Decode varint using 7-bit encoding *)
	REPEAT
		IF NOT pb_st_read(stream, ADR(byte_val), 1) THEN
			pb_st_decode_varint := FALSE;
			RETURN;
		END_IF;
		
		(* Add the 7 bits to result *)
		result := result OR SHL(USINT_TO_UDINT(byte_val AND 16#7F), bitpos);
		bitpos := bitpos + 7;
		
		(* Check if we have more bytes (continuation bit set) *)
		IF (byte_val AND 16#80) = 0 THEN
			EXIT; (* No more bytes *)
		END_IF;
		
		(* Prevent overflow - max 5 bytes for 32-bit value *)
		IF bitpos >= 32 THEN
			stream.errmsg := 'Varint overflow';
			pb_st_decode_varint := FALSE;
			RETURN;
		END_IF;
		
	UNTIL FALSE END_REPEAT;
	
	dest := result;
	pb_st_decode_varint := TRUE;
	
END_FUNCTION

FUNCTION pb_st_encode_svarint
	
	(* ZigZag encode: (n << 1) ^ (n >> 31) *)
	IF value >= 0 THEN
		encoded := SHL(DINT_TO_UDINT(value), 1);
	ELSE
		encoded := SHL(DINT_TO_UDINT(value), 1) XOR 16#FFFFFFFF;
	END_IF;
	
	pb_st_encode_svarint := pb_st_encode_varint(stream, encoded);
	
END_FUNCTION

FUNCTION pb_st_decode_svarint
	
	IF NOT pb_st_decode_varint(stream, ADR(encoded)) THEN
		pb_st_decode_svarint := FALSE;
		RETURN;
	END_IF;
	
	(* ZigZag decode: (n >> 1) ^ (-(n & 1)) *)
	IF (encoded AND 1) = 0 THEN
		dest := UDINT_TO_DINT(SHR(encoded, 1));
	ELSE
		dest := UDINT_TO_DINT(SHR(encoded, 1)) XOR UDINT_TO_DINT(16#FFFFFFFF);
	END_IF;
	
	pb_st_decode_svarint := TRUE;
	
END_FUNCTION

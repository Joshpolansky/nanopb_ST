(* nanoPB stream functions *)
(* Ported from nanoPB C library to B&R IEC 61131-3 ST *)

FUNCTION pb_st_istream_from_buffer
	
	(* Initialize input stream from buffer *)
	stream.state := ADR(buf); (* Store buffer pointer in state *)
	stream.bytes_left := bufsize;
	stream.errmsg := '';
	
	pb_st_istream_from_buffer := ADR(stream);
	
END_FUNCTION

FUNCTION pb_st_ostream_from_buffer
	
	(* Initialize output stream from buffer *)
	stream.state := ADR(buf); (* Store buffer pointer in state *)
	stream.max_size := bufsize;
	stream.bytes_written := 0;
	stream.errmsg := '';
	
	pb_st_ostream_from_buffer := ADR(stream);
	
END_FUNCTION

FUNCTION pb_st_read
	
	(* Check if we have enough bytes *)
	IF stream.bytes_left < count THEN
		stream.errmsg := PB_ERR_EOF;
		pb_st_read := FALSE;
		RETURN;
	END_IF;
	
	(* Copy bytes from stream buffer to destination *)
	src_ptr ACCESS stream.state;
	dest_ptr ACCESS buf;
	
	(* Use brsmemcpy for efficient memory copying *)
	brsmemcpy(ADR(dest_ptr), ADR(src_ptr), count);
	
	(* Update stream position *)
	stream.state := stream.state + count;
	stream.bytes_left := stream.bytes_left - count;
	
	pb_st_read := TRUE;
	
END_FUNCTION

FUNCTION pb_st_write
	
	(* Check if we have enough space *)
	IF stream.bytes_written + count > stream.max_size THEN
		stream.errmsg := PB_ERR_BUFFER_OVERFLOW;
		pb_st_write := FALSE;
		RETURN;
	END_IF;
	
	(* Copy bytes from source to stream buffer *)
//	src_ptr ACCESS buf;
//	dest_ptr ACCESS stream.buffer + stream.bytes_written;
	
	(* Use brsmemcpy for efficient memory copying *)
	brsmemcpy(stream.state, buf, count);
	stream.state := stream.state + count;
	(* Update stream position *)
	stream.bytes_written := stream.bytes_written + count;
	
	pb_st_write := TRUE;
	
END_FUNCTION

FUNCTION pb_st_make_string_substream
	
	(* First decode the string length *)
	IF NOT pb_st_decode_varint(stream, ADR(length)) THEN
		pb_st_make_string_substream := FALSE;
		RETURN;
	END_IF;
	
	(* Check if we have enough data *)
	IF stream.bytes_left < UDINT_TO_UINT(length) THEN
		stream.errmsg := PB_ERR_EOF;
		pb_st_make_string_substream := FALSE;
		RETURN;
	END_IF;
	
	(* Initialize substream from current position *)
	substream.state := stream.state;
	substream.bytes_left := UDINT_TO_UINT(length);
	substream.errmsg := '';
	
	(* Advance main stream *)
	stream.state := stream.state + UDINT_TO_UINT(length);
	stream.bytes_left := stream.bytes_left - UDINT_TO_UINT(length);
	
	pb_st_make_string_substream := TRUE;
	
END_FUNCTION

FUNCTION pb_st_close_string_substream
	
	(* Skip any remaining bytes in substream *)
	IF substream.bytes_left > 0 THEN
		substream.state := substream.state + substream.bytes_left;
		substream.bytes_left := 0;
	END_IF;
	
	pb_st_close_string_substream := TRUE;
	
END_FUNCTION


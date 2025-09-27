
PROGRAM _INIT

    (* Initialize message descriptors with runtime addressing *)
    (* Initialize SensorReading message descriptor *)
	SensorReading_descriptor.field_info := ADR(SensorReading_field_info);
	SensorReading_descriptor.field_count := 7;
	SensorReading_descriptor.submsg_info := 0;
	SensorReading_descriptor.default_value := 0;
	SensorReading_descriptor.callback := 0;
	SensorReading_descriptor.required_field_count := 7;
	SensorReading_descriptor.largest_tag := 7;

	(* Initialize ControlCommand message descriptor *)
	ControlCommand_descriptor.field_info := ADR(ControlCommand_field_info);
	ControlCommand_descriptor.field_count := 6;
	ControlCommand_descriptor.submsg_info := 0;
	ControlCommand_descriptor.default_value := 0;
	ControlCommand_descriptor.callback := 0;
	ControlCommand_descriptor.required_field_count := 6;
	ControlCommand_descriptor.largest_tag := 6;

	(* Initialize SystemStatus message descriptor *)
	SystemStatus_descriptor.field_info := ADR(SystemStatus_field_info);
	SystemStatus_descriptor.field_count := 7;
	SystemStatus_descriptor.submsg_info := ADR(SystemStatus_submsg_info);
	SystemStatus_submsg_info[0] := ADR(SensorReading_descriptor);
	SystemStatus_descriptor.default_value := 0;
	SystemStatus_descriptor.callback := 0;
	SystemStatus_descriptor.required_field_count := 7;
	SystemStatus_descriptor.largest_tag := 7;
	
END_PROGRAM

PROGRAM _CYCLIC
	
	ControlCommand;
	SystemStatus;
	 
END_PROGRAM

PROGRAM _EXIT
	(* Insert code here *)
	 
END_PROGRAM


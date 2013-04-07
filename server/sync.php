<?php
	$user = isset( $_POST['user'] ) ? trim( $_POST['user'] ) : false;
	if( !$user ){
		exit();
	}

	$user = escapeshellarg( $user );
	$file_name = "data/{$user}.json";
	$map = @json_decode( $_POST['task'], true );
	if( file_exists( $file_name ) ){
		$data = @json_decode( file_get_contents( $file_name ), true );
	} else {
		$data = array();
	}
	foreach( $map as $key => $value ){
		if( $value === false ){
			unset( $data[$key] );
		} else {
			$data[$key] = $value;
		}
	}
	$result = json_encode( $data );
	file_put_contents( $file_name, $result );
	echo $result;

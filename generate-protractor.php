<?php
/**
 * Arc Protractor Generator - Backend Script
 * 
 * This script receives form data and executes the Python protractor generator.
 * 
 * INSTALLATION:
 * Place this file in /protractor/ directory along with arc_protractor_generator.py
 * The script uses __DIR__ to find the Python script in the same directory.
 */

// Security headers
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: SAMEORIGIN');

// Only allow POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Configuration
$PYTHON_PATH = '/usr/bin/python3';  // Adjust if needed
$SCRIPT_PATH = __DIR__ . '/arc_protractor_generator.py';  // Script is in same directory
$TEMP_DIR = sys_get_temp_dir();

// Validate required parameters
if (!isset($_POST['pivot_distance']) || empty($_POST['pivot_distance'])) {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Pivot-to-spindle distance is required']);
    exit;
}

// Sanitize and validate inputs
$pivot_distance = filter_var($_POST['pivot_distance'], FILTER_VALIDATE_FLOAT);
$alignment = isset($_POST['alignment']) ? $_POST['alignment'] : 'baerwald';
$turntable_name = isset($_POST['turntable_name']) ? $_POST['turntable_name'] : '';
$paper_size = isset($_POST['paper_size']) ? $_POST['paper_size'] : 'A4';
$inner_groove = isset($_POST['inner_groove']) ? filter_var($_POST['inner_groove'], FILTER_VALIDATE_FLOAT) : null;
$outer_groove = isset($_POST['outer_groove']) ? filter_var($_POST['outer_groove'], FILTER_VALIDATE_FLOAT) : null;
$inner_null = isset($_POST['inner_null']) ? filter_var($_POST['inner_null'], FILTER_VALIDATE_FLOAT) : null;
$outer_null = isset($_POST['outer_null']) ? filter_var($_POST['outer_null'], FILTER_VALIDATE_FLOAT) : null;

// Validate pivot distance range
if ($pivot_distance === false || $pivot_distance < 150 || $pivot_distance > 300) {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Invalid pivot-to-spindle distance. Must be between 150-300mm']);
    exit;
}

// Validate alignment type
$valid_alignments = ['baerwald', 'lofgren_b', 'stevenson', 'custom'];
if (!in_array($alignment, $valid_alignments)) {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Invalid alignment type']);
    exit;
}

// Validate paper size
$valid_paper_sizes = ['A4', 'US', 'letter'];
if (!in_array($paper_size, $valid_paper_sizes)) {
    http_response_code(400);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Invalid paper size']);
    exit;
}

// Validate custom null points if custom alignment
if ($alignment === 'custom') {
    if ($inner_null === null || $inner_null === false || $outer_null === null || $outer_null === false) {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Custom alignment requires both inner and outer null points']);
        exit;
    }
    
    // Validate null points are within reasonable absolute ranges
    if ($inner_null < 40 || $inner_null > 160) {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Inner null point must be between 40-160mm']);
        exit;
    }
    if ($outer_null < 40 || $outer_null > 160) {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Outer null point must be between 40-160mm']);
        exit;
    }
    
    // Validate null points relative to each other
    if ($inner_null >= $outer_null) {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Inner null point (' . $inner_null . 'mm) must be less than outer null point (' . $outer_null . 'mm)']);
        exit;
    }
    
    // Validate null points relative to groove boundaries if provided
    if ($inner_groove !== null && $inner_groove !== false) {
        if ($inner_null <= $inner_groove) {
            http_response_code(400);
            header('Content-Type: application/json');
            echo json_encode(['error' => 'Inner null point (' . $inner_null . 'mm) must be greater than inner groove radius (' . $inner_groove . 'mm)']);
            exit;
        }
    }
    
    if ($outer_groove !== null && $outer_groove !== false) {
        if ($outer_null >= $outer_groove) {
            http_response_code(400);
            header('Content-Type: application/json');
            echo json_encode(['error' => 'Outer null point (' . $outer_null . 'mm) must be less than outer groove radius (' . $outer_groove . 'mm)']);
            exit;
        }
    }
}

// Validate groove values if provided
if ($inner_groove !== null && $inner_groove !== false) {
    if ($inner_groove < 40 || $inner_groove > 100) {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Inner groove radius must be between 40-100mm']);
        exit;
    }
}

if ($outer_groove !== null && $outer_groove !== false) {
    if ($outer_groove < 70 || $outer_groove > 160) {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Outer groove radius must be between 70-160mm']);
        exit;
    }
}

// Validate that inner groove is less than outer groove
if ($inner_groove !== null && $inner_groove !== false && 
    $outer_groove !== null && $outer_groove !== false) {
    if ($inner_groove >= $outer_groove) {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Inner groove radius (' . $inner_groove . 'mm) must be less than outer groove radius (' . $outer_groove . 'mm)']);
        exit;
    }
}

// Generate unique filename
$output_filename = $TEMP_DIR . '/protractor_' . uniqid() . '.pdf';

// Build command
$command = escapeshellcmd($PYTHON_PATH) . ' ' . escapeshellarg($SCRIPT_PATH);
$command .= ' ' . escapeshellarg($pivot_distance);

// Use custom nulls or alignment
if ($alignment === 'custom') {
    $command .= ' --custom-nulls ' . escapeshellarg($inner_null) . ' ' . escapeshellarg($outer_null);
} else {
    $command .= ' --alignment ' . escapeshellarg($alignment);
}

$command .= ' --papersize ' . escapeshellarg($paper_size);
$command .= ' -o ' . escapeshellarg($output_filename);

if (!empty($turntable_name)) {
    $command .= ' --name ' . escapeshellarg($turntable_name);
}

if ($inner_groove !== null && $inner_groove !== false) {
    $command .= ' --inner-groove ' . escapeshellarg($inner_groove);
}

if ($outer_groove !== null && $outer_groove !== false) {
    $command .= ' --outer-groove ' . escapeshellarg($outer_groove);
}

// Execute the Python script
$output = [];
$return_code = 0;
exec($command . ' 2>&1', $output, $return_code);

// Check if execution was successful
if ($return_code !== 0 || !file_exists($output_filename)) {
    http_response_code(500);
    header('Content-Type: application/json');
    $error_message = 'Failed to generate protractor';
    if (!empty($output)) {
        $error_message .= ': ' . implode("\n", $output);
    }
    echo json_encode(['error' => $error_message]);
    
    // Clean up
    if (file_exists($output_filename)) {
        unlink($output_filename);
    }
    exit;
}

// Send the PDF file
header('Content-Type: application/pdf');
header('Content-Disposition: attachment; filename="arc_protractor.pdf"');
header('Content-Length: ' . filesize($output_filename));
header('Cache-Control: no-cache, must-revalidate');
header('Pragma: no-cache');

readfile($output_filename);

// Clean up temporary file
unlink($output_filename);
exit;
?>

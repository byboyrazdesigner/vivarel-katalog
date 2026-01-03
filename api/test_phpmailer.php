<?php
echo json_encode([
    "status" => "ok",
    "message" => "PHPMailer test dosyası çalışıyor!",
    "time" => date('Y-m-d H:i:s'),
    "files" => [
        "PHPMailer.php" => file_exists(__DIR__ . '/PHPMailer.php'),
        "SMTP.php" => file_exists(__DIR__ . '/SMTP.php'),
        "Exception.php" => file_exists(__DIR__ . '/Exception.php')
    ]
]);
?>

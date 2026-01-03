<?php
// mail_cart.php - MailHog Test Versiyonu
header('Content-Type: application/json');
error_reporting(E_ALL);
ini_set('display_errors', 1);

// CORS
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Method not allowed']);
    exit;
}

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || !isset($data['name']) || !isset($data['email']) || !isset($data['cart'])) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Invalid data']);
    exit;
}

$customerName = htmlspecialchars($data['name']);
$customerEmail = htmlspecialchars($data['email']);
$customerPhone = htmlspecialchars($data['phone'] ?? '');
$customerAddress = htmlspecialchars($data['address'] ?? '');
$customerNote = htmlspecialchars($data['note'] ?? '');
$cart = $data['cart'];

// MailHog SMTP fonksiyonu
function sendMailViaMailHog($to, $subject, $body, $replyTo = '') {
    $smtp = @fsockopen('localhost', 1025, $errno, $errstr, 10);
    
    if (!$smtp) {
        error_log("MailHog bağlantı hatası: $errstr ($errno)");
        return false;
    }
    
    fgets($smtp, 515); // 220 response
    
    fwrite($smtp, "HELO localhost\r\n");
    fgets($smtp, 515);
    
    fwrite($smtp, "MAIL FROM:<katalog@localhost>\r\n");
    fgets($smtp, 515);
    
    fwrite($smtp, "RCPT TO:<{$to}>\r\n");
    fgets($smtp, 515);
    
    fwrite($smtp, "DATA\r\n");
    fgets($smtp, 515);
    
    $message = "From: katalog@localhost\r\n";
    $message .= "To: {$to}\r\n";
    if ($replyTo) {
        $message .= "Reply-To: {$replyTo}\r\n";
    }
    $message .= "Subject: {$subject}\r\n";
    $message .= "MIME-Version: 1.0\r\n";
    $message .= "Content-type: text/html; charset=UTF-8\r\n";
    $message .= "\r\n";
    $message .= $body;
    $message .= "\r\n.\r\n";
    
    fwrite($smtp, $message);
    $response = fgets($smtp, 515);
    
    fwrite($smtp, "QUIT\r\n");
    fclose($smtp);
    
    return strpos($response, '250') !== false;
}

// Mail içeriği
$subject = 'Yeni Sipariş - ' . $customerName;
$body = '<html><body style="font-family:Arial,sans-serif;color:#333">';
$body .= '<div style="max-width:600px;margin:0 auto;padding:20px;border:1px solid #ddd">';
$body .= '<h1 style="color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:10px">📦 Yeni Sipariş</h1>';
$body .= '<p><strong>Tarih:</strong> ' . date('d.m.Y H:i:s') . '</p>';
$body .= '<hr style="border:1px solid #eee">';
$body .= '<h2 style="color:#34495e">👤 Müşteri Bilgileri</h2>';
$body .= '<table style="width:100%;margin-bottom:20px">';
$body .= '<tr><td style="padding:5px"><strong>Ad Soyad:</strong></td><td>' . $customerName . '</td></tr>';
$body .= '<tr><td style="padding:5px"><strong>E-posta:</strong></td><td>' . $customerEmail . '</td></tr>';
if ($customerPhone) {
    $body .= '<tr><td style="padding:5px"><strong>Telefon:</strong></td><td>' . $customerPhone . '</td></tr>';
}
if ($customerAddress) {
    $body .= '<tr><td style="padding:5px"><strong>Adres:</strong></td><td>' . $customerAddress . '</td></tr>';
}
if ($customerNote) {
    $body .= '<tr><td style="padding:5px"><strong>Not:</strong></td><td>' . $customerNote . '</td></tr>';
}
$body .= '</table>';
$body .= '<hr style="border:1px solid #eee">';
$body .= '<h2 style="color:#34495e">🛒 Sipariş Detayları</h2>';
$body .= '<table border="1" cellpadding="10" cellspacing="0" style="width:100%;border-collapse:collapse">';
$body .= '<thead><tr style="background:#3498db;color:white">';
$body .= '<th style="text-align:left">Ürün Kodu</th>';
$body .= '<th style="text-align:left">Ürün Adı</th>';
$body .= '<th style="text-align:center">Adet</th>';
$body .= '</tr></thead>';
$body .= '<tbody>';

foreach ($cart as $item) {
    $body .= '<tr>';
    $body .= '<td style="padding:8px">' . htmlspecialchars($item['sku']) . '</td>';
    $body .= '<td style="padding:8px">' . htmlspecialchars($item['name']) . '</td>';
    $body .= '<td style="padding:8px;text-align:center">' . intval($item['quantity']) . '</td>';
    $body .= '</tr>';
}

$body .= '</tbody></table>';
$body .= '<hr style="border:1px solid #eee;margin-top:20px">';
$body .= '<p style="color:#7f8c8d;font-size:12px">Bu mail otomatik olarak oluşturulmuştur.</p>';
$body .= '</div></body></html>';

// Mail gönder
$companyResult = sendMailViaMailHog('info@muratboyraz.com', $subject, $body, $customerEmail);
$customerResult = sendMailViaMailHog($customerEmail, 'Siparişiniz Alındı', $body);

$response = [
    'ok' => $companyResult || $customerResult,
    'debug' => [
        'company' => $companyResult,
        'customer' => $customerResult,
        'mailhog' => true
    ]
];

echo json_encode($response);
?>

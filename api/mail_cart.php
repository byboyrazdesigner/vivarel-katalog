<?php
// Mail gönderimi - Vivarel SMTP
ini_set('display_errors', 0);
error_reporting(E_ALL);

header('Content-Type: application/json; charset=UTF-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

function bad($msg, $code=400){ 
    http_response_code($code); 
    echo json_encode(["ok"=>false,"message"=>$msg]); 
    exit; 
}

// SMTP mail gönderme fonksiyonu
function sendMailViaSMTP($to, $subject, $body, $replyTo = '') {
    $host = 'mail.vivarel.com.tr';
    $port = 587; // TLS port
    $username = 'katalog@vivarel.com.tr';
    $password = 'katalog2024'; // Gerçek şifrenizi buraya yazın
    
    $smtp = @fsockopen($host, $port, $errno, $errstr, 30);
    
    if (!$smtp) {
        error_log("SMTP bağlantı hatası: $errstr ($errno)");
        return false;
    }
    
    $response = fgets($smtp, 515);
    if (strpos($response, '220') === false) {
        fclose($smtp);
        return false;
    }
    
    // EHLO
    fwrite($smtp, "EHLO vivarel.com.tr\r\n");
    $response = fgets($smtp, 515);
    
    // STARTTLS
    fwrite($smtp, "STARTTLS\r\n");
    $response = fgets($smtp, 515);
    if (strpos($response, '220') === false) {
        fclose($smtp);
        return false;
    }
    
    // TLS aktif et
    if (!stream_socket_enable_crypto($smtp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) {
        fclose($smtp);
        return false;
    }
    
    // EHLO again after TLS
    fwrite($smtp, "EHLO vivarel.com.tr\r\n");
    $response = fgets($smtp, 515);
    
    // AUTH LOGIN
    fwrite($smtp, "AUTH LOGIN\r\n");
    fgets($smtp, 515);
    
    fwrite($smtp, base64_encode($username) . "\r\n");
    fgets($smtp, 515);
    
    fwrite($smtp, base64_encode($password) . "\r\n");
    $response = fgets($smtp, 515);
    
    if (strpos($response, '235') === false) {
        error_log("SMTP kimlik doğrulama başarısız: $response");
        fclose($smtp);
        return false;
    }
    
    // MAIL FROM
    fwrite($smtp, "MAIL FROM:<{$username}>\r\n");
    fgets($smtp, 515);
    
    // RCPT TO
    fwrite($smtp, "RCPT TO:<{$to}>\r\n");
    fgets($smtp, 515);
    
    // DATA
    fwrite($smtp, "DATA\r\n");
    fgets($smtp, 515);
    
    // Headers + Body
    $message = "From: {$username}\r\n";
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
    
    // QUIT
    fwrite($smtp, "QUIT\r\n");
    fclose($smtp);
    
    return strpos($response, '250') !== false;
}

$raw = file_get_contents('php://input');
if (!$raw) bad("Boş istek.");

$data = json_decode($raw, true);
if (!$data) bad("JSON okunamadı.");

$senderName = trim($data['sender_name'] ?? '');
$senderCompany = trim($data['sender_company'] ?? '');
$senderPhone = trim($data['sender_phone'] ?? '');
$senderEmail = filter_var($data['sender_email'] ?? '', FILTER_VALIDATE_EMAIL);
$code = preg_replace('/[^A-Z0-9\-]/', '', $data['order_code'] ?? '');

if (!$senderName) bad("Ad Soyad zorunludur.");
if (!$senderCompany) bad("Firma ismi zorunludur.");
if (!$senderPhone) bad("Telefon zorunludur.");
if (!$senderEmail) bad("Geçerli e-posta adresi gereklidir.");

$items = $data['items'] ?? [];
if (empty($items)) bad("Sepet boş.");

$rows = "";
$total = 0;
foreach ($items as $it) {
    $sku = htmlspecialchars($it['sku'] ?? '', ENT_QUOTES, 'UTF-8');
    $name = htmlspecialchars($it['name'] ?? '', ENT_QUOTES, 'UTF-8');
    $brand = htmlspecialchars($it['brand'] ?? '', ENT_QUOTES, 'UTF-8');
    $qty = intval($it['qty'] ?? 1);
    $price = floatval($it['price_value'] ?? 0);
    $line = $qty * $price;
    $total += $line;
    
    $rows .= "<tr><td style='padding:8px;border:1px solid #ddd'>{$sku}</td><td style='padding:8px;border:1px solid #ddd'>{$brand}</td><td style='padding:8px;border:1px solid #ddd'>{$name}</td><td style='padding:8px;border:1px solid #ddd;text-align:right'>{$qty}</td><td style='padding:8px;border:1px solid #ddd;text-align:right'>" . number_format($price, 2, ',', '.') . " TL</td><td style='padding:8px;border:1px solid #ddd;text-align:right'>" . number_format($line, 2, ',', '.') . " TL</td></tr>";
}

$body = "<div style='font-family:Arial,sans-serif;max-width:800px'><h2>🛒 Yeni Sepet Talebi</h2><p><strong>Talep Kodu:</strong> {$code}</p><hr><h3>Müşteri Bilgileri</h3><p><strong>Ad Soyad:</strong> {$senderName}</p><p><strong>Firma:</strong> {$senderCompany}</p><p><strong>Telefon:</strong> {$senderPhone}</p><p><strong>E-posta:</strong> {$senderEmail}</p><h3>Sipariş Detayları</h3><table style='width:100%;border-collapse:collapse'><thead><tr style='background:#f5f5f5'><th style='padding:8px;border:1px solid #ddd;text-align:left'>SKU</th><th style='padding:8px;border:1px solid #ddd;text-align:left'>Marka</th><th style='padding:8px;border:1px solid #ddd;text-align:left'>Ürün</th><th style='padding:8px;border:1px solid #ddd;text-align:right'>Adet</th><th style='padding:8px;border:1px solid #ddd;text-align:right'>Birim Fiyat</th><th style='padding:8px;border:1px solid #ddd;text-align:right'>Toplam</th></tr></thead><tbody>{$rows}</tbody><tfoot><tr><td colspan='5' style='padding:8px;border:1px solid #ddd;text-align:right'><strong>Genel Toplam</strong></td><td style='padding:8px;border:1px solid #ddd;text-align:right'><strong>" . number_format($total, 2, ',', '.') . " TL</strong></td></tr></tfoot></table><p style='margin-top:20px;color:#999;font-size:12px'>Gönderim: " . date('d.m.Y H:i:s') . "</p></div>";

$subject = "B2B Sepet Talebi: {$code}";

// Firmaya gönder
$sent1 = sendMailViaSMTP("info@muratboyraz.com", $subject, $body, $senderEmail);
error_log("MAIL TO COMPANY: " . ($sent1 ? "SUCCESS" : "FAILED"));

// Müşteriye gönder
$sent2 = sendMailViaSMTP($senderEmail, $subject, $body);
error_log("MAIL TO CUSTOMER ({$senderEmail}): " . ($sent2 ? "SUCCESS" : "FAILED"));

if ($sent1 || $sent2) {
    echo json_encode(["ok" => true, "message" => "Talebiniz alındı.", "order_code" => $code, "debug" => ["company" => $sent1, "customer" => $sent2]]);
} else {
    error_log("MAIL TOTAL FAILURE for {$code}");
    bad("E-posta gönderilemedi. Lütfen daha sonra tekrar deneyin.", 500);
}

if ($sent1 || $sent2) {
    echo json_encode(["ok" => true, "message" => "Talebiniz alındı.", "order_code" => $code, "debug" => ["company" => $sent1, "customer" => $sent2]]);
} else {
    error_log("MAIL TOTAL FAILURE for {$code}");
    bad("E-posta gönderilemedi. Sunucu mail ayarlarını kontrol edin.", 500);
}

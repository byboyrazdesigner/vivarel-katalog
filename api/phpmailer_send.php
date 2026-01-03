<?php
// PHPMailer ile SMTP üzerinden mail gönderimi
require 'PHPMailer.php';
require 'SMTP.php';
require 'Exception.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
use PHPMailer\PHPMailer\SMTP;

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

$mailEnv = strtolower(trim($data['mail_env'] ?? ($_SERVER['HTTP_X_MAIL_ENV'] ?? getenv('MAIL_ENV') ?? '')));
if (!in_array($mailEnv, ['prod', 'test'], true)) {
    $mailEnv = 'prod';
}

$mailConfigs = [
    'prod' => [
        'host' => 'mail.vivarel.com.tr',
        'port' => 465,
        'secure' => PHPMailer::ENCRYPTION_SMTPS,
        'auth' => true,
        'username' => 'katalog@vivarel.com.tr',
        'password' => 'aBuTGXiN.hjxLs2',
        'auto_tls' => true,
        'from_email' => 'katalog@vivarel.com.tr',
        'from_name' => 'TEM Katalog',
    ],
    'test' => [
        'host' => 'localhost',
        'port' => 1025,
        'secure' => false,
        'auth' => false,
        'username' => '',
        'password' => '',
        'auto_tls' => false,
        'from_email' => 'katalog@vivarel.com.tr',
        'from_name' => 'TEM Katalog (Test)',
    ],
];

$activeConfig = $mailConfigs[$mailEnv];

if (!function_exists('buildMailer')) {
function buildMailer(array $cfg): PHPMailer {
    $mail = new PHPMailer(true);
    $mail->isSMTP();
    $mail->Host = $cfg['host'];
    $mail->Port = $cfg['port'];
    $mail->CharSet = 'UTF-8';
    $mail->SMTPAuth = !empty($cfg['auth']);
    if ($mail->SMTPAuth) {
        $mail->Username = $cfg['username'];
        $mail->Password = $cfg['password'];
    } else {
        $mail->Username = '';
        $mail->Password = '';
    }

    if (!empty($cfg['secure'])) {
        $mail->SMTPSecure = $cfg['secure'];
    } else {
        $mail->SMTPSecure = false;
        $mail->SMTPAutoTLS = false;
    }

    if (array_key_exists('auto_tls', $cfg)) {
        $mail->SMTPAutoTLS = (bool)$cfg['auto_tls'];
    }

    $fromEmail = $cfg['from_email'] ?? 'katalog@vivarel.com.tr';
    $fromName = $cfg['from_name'] ?? 'TEM Katalog';
    $mail->setFrom($fromEmail, $fromName);

    return $mail;
}
}

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

    $imageRaw = trim($it['image'] ?? '');
    $imageCell = "<span style='color:#999;font-size:12px'>—</span>";
    if ($imageRaw !== '') {
        $imageUrl = htmlspecialchars($imageRaw, ENT_QUOTES, 'UTF-8');
        $imageCell = "<img src='{$imageUrl}' alt='{$name}' width='80' height='80' style='display:block;width:80px;height:80px;max-width:80px;max-height:80px;object-fit:contain;border-radius:6px;border:1px solid #ddd;background:#fff;padding:4px;margin:0 auto' />";
    }

    $rows .= "<tr><td style='padding:8px;border:1px solid #ddd;text-align:center'>{$imageCell}</td><td style='padding:8px;border:1px solid #ddd'>{$sku}</td><td style='padding:8px;border:1px solid #ddd'>{$brand}</td><td style='padding:8px;border:1px solid #ddd'>{$name}</td><td style='padding:8px;border:1px solid #ddd;text-align:right'>{$qty}</td><td style='padding:8px;border:1px solid #ddd;text-align:right'>" . number_format($price, 2, ',', '.') . " TL</td><td style='padding:8px;border:1px solid #ddd;text-align:right'>" . number_format($line, 2, ',', '.') . " TL</td></tr>";
}

$body = "<div style='font-family:Arial,sans-serif;max-width:800px'><h2>🛒 Yeni Sepet Talebi</h2><p><strong>Talep Kodu:</strong> {$code}</p><hr><h3>Müşteri Bilgileri</h3><p><strong>Ad Soyad:</strong> {$senderName}</p><p><strong>Firma:</strong> {$senderCompany}</p><p><strong>Telefon:</strong> {$senderPhone}</p><p><strong>E-posta:</strong> {$senderEmail}</p><h3>Sipariş Detayları</h3><table style='width:100%;border-collapse:collapse'><thead><tr style='background:#f5f5f5'><th style='padding:8px;border:1px solid #ddd;text-align:center'>Görsel</th><th style='padding:8px;border:1px solid #ddd;text-align:left'>SKU</th><th style='padding:8px;border:1px solid #ddd;text-align:left'>Marka</th><th style='padding:8px;border:1px solid #ddd;text-align:left'>Ürün</th><th style='padding:8px;border:1px solid #ddd;text-align:right'>Adet</th><th style='padding:8px;border:1px solid #ddd;text-align:right'>KDV Dahil Birim Fiyat</th><th style='padding:8px;border:1px solid #ddd;text-align:right'>Toplam</th></tr></thead><tbody>{$rows}</tbody><tfoot><tr><td colspan='6' style='padding:8px;border:1px solid #ddd;text-align:right'><strong>Genel Toplam</strong></td><td style='padding:8px;border:1px solid #ddd;text-align:right'><strong>" . number_format($total, 2, ',', '.') . " TL</strong></td></tr></tfoot></table><p style='margin-top:10px;font-size:13px;color:#666;'><strong>Not:</strong> Fiyatlara KDV dahildir.</p><p style='margin-top:20px;color:#999;font-size:12px'>Gönderim: " . date('d.m.Y H:i:s') . "</p></div>";

$mail = buildMailer($activeConfig);
try {
    $mail->Timeout = 30;
    $mail->addAddress('katalog@vivarel.com.tr'); // Firma
    $mail->addReplyTo($senderEmail, $senderName);
    $mail->Subject = "B2B Sepet Talebi: {$code}";
    $mail->isHTML(true);
    $mail->Body = $body;
    $mail->send();
    $ok1 = true;
} catch (Exception $e) {
    $ok1 = false;
    error_log('Firma maili gönderilemedi: ' . $mail->ErrorInfo);
}

// Müşteriye de gönder
$mail2 = buildMailer($activeConfig);
try {
    $mail2->Timeout = 30;
    $mail2->addAddress($senderEmail);
    $mail2->addReplyTo('katalog@vivarel.com.tr', 'TEM Katalog');
    $mail2->Subject = "B2B Sepet Talebiniz: {$code}";
    $mail2->isHTML(true);
    $mail2->Body = $body;
    $mail2->send();
    $ok2 = true;
} catch (Exception $e) {
    $ok2 = false;
    error_log('Müşteri maili gönderilemedi: ' . $mail2->ErrorInfo);
}

if ($ok1 || $ok2) {
    echo json_encode(["ok" => true, "message" => "Talebiniz alındı.", "order_code" => $code, "debug" => ["company" => $ok1, "customer" => $ok2, "env" => $mailEnv]]);
} else {
    bad("E-posta gönderilemedi. Sunucu mail ayarlarını kontrol edin.", 500);
}
?>

<?php

require_once("../inc/util.inc");
require_once("../inc/xml.inc");

xml_header();

$config = get_config();
$long_name = parse_config($config, "<long_name>");
$min_passwd_length = parse_config($config, "<min_passwd_length>");
if (!$min_passwd_length) {
    $min_passwd_length = 6;
}
$disable_account_creation = parse_bool($config, "disable_account_creation");
$client_account_creation_disabled = parse_bool($config, "client_account_creation_disabled");

echo "<project_config>
    <name>$long_name</name>
";

if ($disable_account_creation) {
    echo "    <account_creation_disabled/>\n";
}
if ($client_account_creation_disabled) {
    echo "    <client_account_creation_disabled/>\n";
}
echo "
    <min_passwd_length>$min_passwd_length</min_passwd_length>
</project_config>
";

?>

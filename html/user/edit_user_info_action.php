<?php

require_once("../inc/db.inc");
require_once("../inc/user.inc");
require_once("../inc/util.inc");
require_once("../inc/countries.inc");

db_init();
$user = get_logged_in_user();

$name = process_user_text(post_str("user_name"));
$url = process_user_text(post_str("url"));
$country = post_str("country");
if (!is_valid_country($country)) {
    echo "bad country";
    exit();
}
$postal_code = process_user_text(post_str("postal_code"));

$result = mysql_query("update user set name='$name', url='$url', country='$country', postal_code='$postal_code' where id=$user->id");
if ($result) {
    Header("Location: home.php");
} else {
    page_head("User info update");
    echo "Couldn't update user info.";
    page_tail();
}

?>

<?php

include_once("util.inc");

page_head("Create account");
?>

<form method=post action=create_account_action.php>

<table cellpadding=8>
<tr><td align=right>
<b>Name or nickname:</b>
<br><font size=-1> Your identifier on our web site.  Use your real name or a nickname.</font>
</td><td>
<input name=new_name size=30>
</td></tr>

<tr><td align=right>
<b>Email address:</b>
<br><font size=-1>Your <b>account key</b> will be emailed to this address.</font>
</td><td>
<input name=new_email_addr size=50>
</td></tr>

<!--
<tr><td align=right>
<b>Password:</b>
<br><font size=-1>Used to log in to your account</font>
</td><td>
<input name=new_password type=password>
</td></tr>
<tr><td align=right>
<b>Retype password to confirm:</b>
</td><td>
<input name=new_password2 type=password>
</td></tr>
-->

<tr><td align=right>
<b>Country:</b>
<br><font size=-1>select the country you wish to represent, if any.</font>
</td><td>
<select name=country>

<?php
print_country_select();
?>
</select>

</td></tr>

<tr><td align=right>
<b>Postal (ZIP) code:</b>
</td><td>
<input name=postal_code size=20>
</td></tr>

<tr><td align=right>
<br>
</td><td>
<input type=submit value="Create account">
</td></tr>
</table>
</form>

<?php
page_tail();

?>

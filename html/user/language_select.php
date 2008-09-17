<?php
// This file is part of BOINC.
// http://boinc.berkeley.edu
// Copyright (C) 2008 University of California
//
// BOINC is free software; you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License
// as published by the Free Software Foundation,
// either version 3 of the License, or (at your option) any later version.
//
// BOINC is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with BOINC.  If not, see <http://www.gnu.org/licenses/>.


require_once("../inc/util.inc");
require_once("../inc/translation.inc");
$imgdir = "img/flags/";


$languages = getSupportedLanguages();
$prefs = $_SERVER["HTTP_ACCEPT_LANGUAGE"];

$set_lang = get_str("set_lang", true);
if ($set_lang){
    if (!in_array($set_lang, $languages) && $set_lang!="auto"){
        error_page("Language not supported");
    } else {
        send_cookie('lang', $set_lang, true);
        header("Location: index.php");
        exit;
    }
}

page_head("Language selection");

echo "
    <p>
    This web site is available in several languages.
    The currently selected language is: <em>".tr(LANG_NAME_INTERNATIONAL)."</em> (".tr(LANG_NAME_NATIVE).").
    <p>
    Normally the choice of language
    is determined by your browser's language setting,
    which is: <b>$prefs</b>.
    You can change this setting using:
    <ul>
    <li>Firefox: Tools/Options/General
    <li>Microsoft IE: Tools/Internet Options/Languages
    </ul>
    <p>
    Or you can select a language by clicking on one of the links.
    This will send your browser a cookie;
    make sure your browser accepts cookies from our domain.
    </p>
";

start_table();
row2("Language symbol", "Language name (click to select)");
row2("",
    "<a href=language_select.php?set_lang=auto>Use browser language setting</a>"
);
for ($i=0; $i<sizeof($languages);$i++){
    $lang_native[$i] = trSpecific(LANG_NAME_NATIVE, $languages[$i]);
    $lang_international[$i] = trSpecific(LANG_NAME_INTERNATIONAL, $languages[$i]);
}

array_multisort($lang_international, $languages, $lang_native);

for ($i=0; $i<sizeof($languages);$i++){
//    if (file_exists($imgdir.$languages[$i].".png")){
//        $im = "<a href=\"language_select.php?set_lang=".$languages[$i]."\"><img src=\"".$imgdir.$languages[$i].".png\" border=0></a>";
//    } else {
//        $im="";
//    }
//    row3($im,
    row2(
        "<a href=\"language_select.php?set_lang=".$languages[$i]."\">".$languages[$i]."</a>",
        "<a href=\"language_select.php?set_lang=".$languages[$i]."\">".$lang_international[$i]."</a>"
    );
}
end_table();
echo "
    <p>
    Translations are done by volunteers.
    If your native language is not here,
    <a href=translate.php>you can help</a>.
";
page_tail();
?>

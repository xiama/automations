<?php

include "Validate.php";

if (Validate::number(8.0004, array('decimal' => '.', 'dec_prec' => 4))) {
    echo 'get_correct_number';
} else {
    echo "Invalid number";
}
?>

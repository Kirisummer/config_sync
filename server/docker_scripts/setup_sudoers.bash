sudoers_file=/etc/sudoers.d/sudo_user_manage
printf '%%%s ALL=(ALL) !ALL\n'                   "$USER_GRP" >> "$sudoers_file"
printf '%%%s ALL=(ALL) !ALL\n'                   "$ADMIN_GRP" >> "$sudoers_file"
printf '%%%s ALL=(ALL) NOPASSWD:PASSWD_CHANGE\n' "$USER_GRP" >> "$sudoers_file"
printf '%%%s ALL=(ALL) NOPASSWD:USER_ADMIN\n'    "$ADMIN_GRP" >> "$sudoers_file"
chmod 440 "$sudoers_file"

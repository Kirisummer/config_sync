mkdir ssh_bin
curl -L %plink% -o ssh_bin\plink.exe
curl -L %git_installer% -o ssh_bin\git_installer.exe
echo Install to ssh_bin\PortableGit - a default option
ssh_bit\git_installer.exe
pyinstaller --add-binary=ssh_bin\plink.exe;ssh_bin --add-binary=ssh_bin\PortableGit\cmd\git.exe;ssh_bin --add-data run.cmd main.py

pushd dist
move main config_client
tar -acf win_config_client.zip config_client
popd

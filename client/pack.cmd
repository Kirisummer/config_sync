del /s /q ssh_bin
mkdir ssh_bin
curl -L https://the.earth.li/~sgtatham/putty/latest/w64/plink.exe -o ssh_bin\plink.exe
curl -L https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.1/PortableGit-2.41.0-64-bit.7z.exe -o ssh_bin\git_installer.exe
echo Install to ssh_bin\PortableGit - a default option
ssh_bin\git_installer.exe
pyinstaller --add-binary=ssh_bin\plink.exe;ssh_bin --add-binary=ssh_bin\PortableGit\cmd\git.exe;ssh_bin --add-data run.cmd;. --noconsole main.py

pushd dist
move main config_client
tar -acf win_config_client.zip config_client
popd

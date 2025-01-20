This repository makes it possible to receive data from unmanned vehicles using Mavproxy and provides a convenient interface.
It is designed to work in WSL 1.









###INSTRUCTION###






1.Install Ubuntu 20.04 or 22.04 wsl instance in Windows.(You can use Microsoft store or do it manually)
  1.1.Open "Turn Windows features on or off" and enable Virtual Machine Platform.
  1.2.Press "OK" and reboot the system.
  1.3.Open "Turn Windows features on or off" and enable Hyper-V.
  1.4.Press "OK" and reboot the system.
  1.5.Open "Turn Windows features on or off" and enable Windows Subsystem For Linux.
  1.6.Press "OK" and reboot the system.
  1.7.Open CMD as Administartor.
  1.8.Write "wsl.exe --install -d <distro>" put Ubuntu version intead of <distro>. example` Ubuntu-20.04 
2.Ensure that wsl version is 1.
  2.1.Open CMD or PowerShell.
  2.2.Write "wsl.exe --set-version <Distro> 1" put Ubuntu version intead of <distro>. example` Ubuntu-20.04
3.Install git in Ubuntu.
4.Ensure that python and pip are installed.
5.Clone github repository.
6.Run "install.sh" as super user with --autorun argument to create servise which run "Drone-managment" application on startup, or without to run it manually. 

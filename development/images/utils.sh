Distro=unknown
Command=$1

distro() {
  echo "Find distro name:"
  Distro=unknown
  while IFS="" read -r p || [ -n "$p" ]
  do
    if [ "$p" = "ID=ubuntu" ]; then
      Distro=debian
    elif [ "$p" = "ID=debian" ]; then
      Distro=debian
    elif [ "$p" = "ID=alpine" ]; then
      Distro=alpine
    fi
  done < /etc/os-release
  echo " - distro is $Distro"
}

user() {
  UserName=$1
  UserId=$2
  GroupName=$3
  GroupId=$4
  Shell=$5

  echo "Create user:"
  echo " - user.id     ${UserId}"
  echo " - user.name   ${UserName}"
  echo " - group.id    ${GroupId}"
  echo " - group.name  ${GroupName}"
  echo " - shell       ${Shell}"
  echo " - sudo        password-free"

  mkdir -p /etc/sudoers.d
  echo "$UserName ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd

  if [ $Distro = "debian" ]; then
    groupadd -g "$GroupId" "$GroupName"
    useradd -m -u "$UserId" -d "/home/$UserName" -g "$GroupId" -s "$Shell" "$UserName"
  elif [ $Distro = "alpine" ]; then
    addgroup -g "$GroupId" "$GroupName"
    adduser -u "$UserId" -G "$GroupName" -s "$Shell" -D -h "/home/$UserName" "$UserName"
  else
    echo "Failed to add user: unknown OS"
  fi

  sudo chown "$UserName:$GroupName" "/home/$UserName"
}

package_manager_update() {
  if [ $Distro = "debian" ]; then
    apt update
  elif [ $Distro = "alpine" ]; then
    apk update
  else
    echo "Failed to update packages: unknown OS"
  fi
}

package_manager_upgrade() {
  if [ $Distro = "debian" ]; then
    apt upgrade -y
  elif [ $Distro = "alpine" ]; then
    apk upgrade
  else
    echo "Failed to upgrade packages: unknown OS"
  fi
}

package_manager_install() {
  if [ $Distro = "debian" ]; then
    apt install -y "$@"
  elif [ $Distro = "alpine" ]; then
    apk add "$@"
  else
    echo "Failed to upgrade by package manager: unknown OS"
  fi
}

distro

if [ "$Command" = "user" ]; then

  # CLI Arguments:
  #  - [0] User name
  #  - [1] User id
  #  - [2] Group name
  #  - [3] Grou id
  #  - [4] Shell
  #
  # Example:
  #  (1) utils.sh user foo 1000 bar 1001 bash

  user "$2" "$3" "$4" "$5" "$6"

elif [ "$Command" = "package" ]; then

  # CLI Arguments:
  #  - [0] sub-command (install, update, upgrade)
  #  - [1] packages
  #
  # Example:
  #  (1) utils.sh package update
  #  (2) utils.sh package upgrade
  #  (3) utils.sh package install zsh
  #  (4) utils.sh package install make cmake git

  subcmd=$2

  if [ "$subcmd" = "update" ]; then
    package_manager_update
  elif [ "$subcmd" = "upgrade" ]; then
    package_manager_upgrade
  elif [ "$subcmd" = "install" ]; then
    package_manager_install "${@:3}"
  else
    echo "Invalid package sub-command: $subcmd"
  fi

else
  echo "Invalid command: $Command"
fi

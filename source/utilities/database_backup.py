from dictionary.vars import operational_system, today, absolute_app_path
from dictionary.vars import db_user, db_password, db_database
from functions.get_actual_time import GetActualTime
from pathlib import Path
from time import sleep
import os
import streamlit as st
import subprocess


class Backup:
    """
    Classe com métodos para realização do backup da base de dados da aplicação.
    """

    def make_backup(self, backup_path: str, operational_system: str = operational_system):
        """
        Realiza o backup da base de dados da aplicação.

        Parameters
        ----------
        backup_path (str): Diretório em qual o backup será salvo.\n
        operational_system (str): Sistema operacional sobre o qual a aplicação está sendo executado.
        """

        time = GetActualTime()
        actual_time = time.get_actual_time()
        actual_time = actual_time.replace(":", "_")

        directory_command = "cd " + backup_path
        backup_archive_name = "backup_{}_{}_{}.sql".format(
            db_database, today, actual_time
        )
        backup_command = "mysqldump -u{} -p{} --databases {} >> {}".format(
            db_user, db_password, db_database, backup_archive_name
        )

        if operational_system == "posix":
            backup_shell_script_name = absolute_app_path + "/services/temp_backup.sh"
            with open(backup_shell_script_name, "w") as backup_archive:
                backup_archive.write("#!/bin/bash")
                backup_archive.write("\n")
                backup_archive.write(directory_command)
                backup_archive.write("\n")
                backup_archive.write("sleep 1")
                backup_archive.write("\n")
                backup_archive.write(backup_command)
                backup_archive.write("\n")
                backup_archive.write("sleep 1")

            modified_archive = Path(backup_shell_script_name)
            modified_archive.chmod(0o777)

            with st.spinner(text="Navegando ao diretório {}...".format(backup_path)):
                sleep(2.5)
            with st.spinner(text="Realizando o backup do arquivo {}...".format(backup_archive_name)):
                sleep(2.5)
            try:
                subprocess.run(["bash", backup_shell_script_name],
                               check=True, text=True, capture_output=True)
                os.remove(backup_shell_script_name)
                absolute_backup_archive_path = backup_path + "/" + backup_archive_name
                modified_backup_archive = Path(absolute_backup_archive_path)
                modified_backup_archive.chmod(0o777)
                st.info(body="O arquivo {} foi salvo no diretório {}.".format(
                    backup_archive_name, backup_path))

            except subprocess.CalledProcessError as error:
                st.error(body="Erro ao executar o script: {}".format(error.stderr))

    def main_menu(self):
        """
        Menu do backup de dados.
        """
        col4, col5 = st.columns(2)

        with col4:
            if operational_system == "posix":
                placeholder_text = "Ex: /home/'usuario'/Downloads"
            elif operational_system == "nt":
                placeholder_text = "Ex: C:\\Users\\usuario\\Downloads"
            with st.expander(label=":floppy_disk: Backup de dados", expanded=True):
                backup_directory = st.text_input(label="Diretório de backup", placeholder=placeholder_text)
            backup_confirm_button = st.button(label=":white_check_mark: Confirmar diretório")

        if backup_confirm_button:
            with col5:
                with st.spinner(text="Aguarde..."):
                    sleep(2.5)

                with st.status(label="Dados", expanded=True):

                    if backup_directory != "":
                        if os.path.exists(backup_directory):
                            self.make_backup(backup_directory)
                        else:
                            st.error(body="O diretório {} não existe em sua máquina. Informe um diretório real.".format(
                                backup_directory))
                    elif backup_directory == "":
                        st.error(body="O caminho do diretório está vazio ou não preenchido.")

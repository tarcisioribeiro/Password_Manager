from dictionary.sql import (
    check_user_bank_accounts_query,
    search_bank_accounts_query
)
from dictionary.vars import (
    financial_institution_list,
    to_remove_list,
    bank_account_field_names
)
from functions.query_executor import QueryExecutor
from functions.login import Login
from time import sleep
import streamlit as st


class BankAccount:
    """
    Classe que representa as contas bancárias,
    com as quatro funções básicas de um CRUD.
    """

    def check_if_bank_account_exists(self, bank_account_name: str):
        """
        Verifica se o nome da conta bancária
        já foi utilizado anteriormente.

        Returns
        -------
        is_bank_account_name_available : bool
            Se o nome de conta bancária está disponível ou não.
        """
        logged_user_name, logged_user_document = Login().get_user_data(
            return_option="user_login_password"
        )

        is_bank_account_name_available: bool

        bank_accounts_with_name_query = """
        SELECT
            COUNT(id_conta)
        FROM
            contas_bancarias
        WHERE
            nome_conta = %s
            AND
                nome_proprietario_conta = %s
            AND
                documento_proprietario_conta = %s;
        """
        query_values = (
            bank_account_name,
            logged_user_name,
            logged_user_document
        )

        bank_accounts_with_name_quantity = (
            QueryExecutor().simple_consult_query(
                query=bank_accounts_with_name_query,
                params=query_values
            )
        )
        bank_accounts_with_name_quantity = QueryExecutor().treat_simple_result(
            value_to_treat=bank_accounts_with_name_quantity,
            values_to_remove=to_remove_list
        )
        bank_accounts_with_name_quantity = int(
            bank_accounts_with_name_quantity
        )

        if bank_accounts_with_name_quantity == 0:
            is_bank_account_name_available = True
        else:
            is_bank_account_name_available = False

        return is_bank_account_name_available

    def get_user_accounts_quantity(self):
        """
        Consulta a quantidade de contas registradas pelo usuário.

        Returns
        -------
        user_accounts_quantity : int
            Quantidade de contas registradas pelo usuário.
        """
        logged_user_name, logged_user_document = (
            Login().get_user_data(
                return_option="user_doc_name"
            )
        )

        user_accounts_quantity = QueryExecutor().simple_consult_query(
            check_user_bank_accounts_query,
            params=(logged_user_name,
                    logged_user_document
                    )
        )
        user_accounts_quantity = (
            QueryExecutor().treat_simple_result(
                user_accounts_quantity,
                to_remove_list
            )
        )
        user_accounts_quantity = int(user_accounts_quantity)

        return user_accounts_quantity

    def get_user_bank_accounts(self):
        """
        Consulta o nome das contas bancárias do usuário.

        Returns
        -------
        bank_accounts : list
            Lista com os nomes das contas bancárias.
        """
        logged_user_name, logged_user_document = (
            Login().get_user_data(
                return_option="user_doc_name"
            )
        )

        user_bank_accounts = []

        bank_accounts = QueryExecutor().complex_consult_query(
            query=search_bank_accounts_query,
            params=(logged_user_name,
                    logged_user_document
                    )
        )
        bank_accounts = QueryExecutor().treat_numerous_simple_result(
            bank_accounts,
            to_remove_list
        )

        for i in range(0, len(bank_accounts)):
            user_bank_accounts.append(bank_accounts[i])

        return bank_accounts

    def create_new_bank_account(self):
        """
        Função para criação de uma nova conta.
        """
        logged_user_name, logged_user_document = Login().get_user_data(
            return_option="user_doc_name"
        )
        logged_user, logged_user_password = Login().get_user_data(
            return_option="user_login_password"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader(body=":computer: Entrada de Dados")
            with st.expander(label="Dados da Conta", expanded=True):
                account_name = st.text_input(
                    label="Nome",
                    max_chars=100,
                    placeholder='Conta',
                    help="""Necessário para identificação.
                    A sugestão é informar algo direto e descritivo,
                    como por exemplo 'Conta Corrente BB'."""
                )
                financial_institution = st.selectbox(
                    label='Instituição',
                    options=financial_institution_list,
                    help='Insituição financeira a qual pertence a conta.'
                )
                financial_institution_code = st.text_input(
                    label="Código da instituição",
                    max_chars=5,
                    help="""Código da insituição financiera no SPB
                    (Sistemas de Pagamentos Brasileiro).
                    """
                )
                agency = st.text_input(
                    label="Agência",
                    max_chars=10,
                    help="Número da agência."
                )

            confirm_data = st.checkbox(label="Confirmar dados")

        with col2:
            st.subheader(body=":white_check_mark: Validação dos Dados")
            with st.expander(label="Dados da Conta", expanded=True):
                account_number = st.text_input(
                    label="Número da conta",
                    max_chars=15,
                    help="Número de identificação da conta."
                )
                account_digit = st.text_input(
                    label="Dígito",
                    max_chars=1,
                    placeholder='0',
                    help='''
                    Dígito identificador da conta.
                    Caso não haja, preencha como 0.
                    '''
                )
                account_password = st.text_input(
                    label="Senha da conta",
                    max_chars=30,
                    type='password',
                    help='''
                    Senha utilizada para saques e demais
                    operações em terminais físicos.
                    '''
                )
                digital_account_password = st.text_input(
                    label="Senha digital da conta",
                    max_chars=30,
                    type='password',
                    help='''
                    Senha digital da conta,
                    utilizada para operações virtuais como Pix.
                    '''
                )

            register_new_account = st.button(
                label=":floppy_disk: Cadastrar conta"
            )

            if confirm_data and register_new_account:
                with col3:
                    with st.spinner(text='Aguarde...'):
                        sleep(2.5)
                is_name_available = self.check_if_bank_account_exists(
                    bank_account_name=account_name
                )

                if is_name_available:
                    with col3:
                        with st.expander(
                            label="Validação de dados",
                            expanded=True
                        ):
                            st.success(body="Nome de conta válida.")

                    insert_password_query = """
                    INSERT INTO
                        contas_bancarias (
                            nome_conta,
                            instituicao_financeira,
                            codigo_instituicao_financeira,
                            agencia,
                            numero_conta,
                            digito_conta,
                            senha_bancaria_conta,
                            senha_digital_conta,
                            nome_proprietario_conta,
                            documento_proprietario_conta
                            )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    query_values = (
                        account_name,
                        financial_institution,
                        financial_institution_code,
                        agency,
                        account_number,
                        account_digit,
                        account_password,
                        digital_account_password,
                        logged_user_name,
                        logged_user_document
                    )
                    QueryExecutor().insert_query(
                        insert_password_query,
                        query_values,
                        'Conta cadastrada com sucesso!',
                        'Erro ao cadastrar conta:'
                    )
                    log_query = '''
                    INSERT INTO
                        logs_atividades (
                            usuario_log,
                            tipo_log,
                            conteudo_log
                        )
                    VALUES (%s, %s, %s)
                    '''
                    log_query_values = (
                        logged_user,
                        'Cadastro',
                        'Cadastrou a conta {}'.format(
                            query_values[0]
                        )
                    )
                    QueryExecutor().insert_query(
                        query=log_query,
                        values=log_query_values,
                        success_message='Log gravado.',
                        error_message='Erro ao gravar log:'
                    )
                else:
                    with col3:
                        st.subheader(
                            body=":white_check_mark: Validação dos Dados"
                        )
                        with st.expander(
                            label="Validação de dados",
                            expanded=True
                        ):
                            st.error(
                                body="O nome da conta já está sendo utilizado."
                            )
            elif register_new_account and confirm_data is False:
                with col3:
                    with st.spinner(text="Aguarde..."):
                        sleep(0.5)
                    st.subheader(
                        body=":white_check_mark: Validação dos Dados"
                    )
                    with st.expander(
                        label="Validação de dados",
                        expanded=True
                    ):
                        st.warning(
                            body="""
                            Você deve confirmar os dados antes de prosseguir.
                            """
                        )

    def read_bank_accounts(self):
        """
        Função para a consulta de uma conta bancária.
        """
        logged_user_name, logged_user_document = Login().get_user_data(
            return_option="user_doc_name"
        )
        logged_user, logged_user_password = Login().get_user_data(
            return_option="user_login_password"
        )
        user_accounts_quantity = self.get_user_accounts_quantity()
        if user_accounts_quantity == 0:
            col1, col2, col3 = st.columns(3)
            with col2:
                st.warning(body="Você ainda não possui contas cadastradas.")
        elif user_accounts_quantity >= 1:
            col1, col2 = st.columns(2)
            user_bank_accounts = self.get_user_bank_accounts()
            with col1:
                st.subheader(body=":computer: Entrada de Dados")
                with st.expander(label="Dados", expanded=True):
                    selected_option = st.selectbox(
                        label="Selecione a conta",
                        options=user_bank_accounts
                    )
                    safe_password = st.text_input(
                        label="Informe sua senha",
                        type="password",
                        help="""
                        Corresponde a senha de acesso.
                        """
                    )
                    confirm_safe_password = st.text_input(
                        label="Confirme sua senha",
                        type="password",
                        help="""
                        Deve ser idêntica a senha informada acima.
                        """
                    )
                    confirm_password_selection = st.checkbox(
                        label="Confirmar seleção"
                    )
                consult_button = st.button(
                    label=":file_folder: Consultar conta"
                )
            account_details_query = '''
            SELECT
                CONCAT('Conta: ',
                        contas_bancarias.nome_conta,
                        ' - Instituição: ',
                        contas_bancarias.instituicao_financeira),
                contas_bancarias.agencia,
                CONCAT('',
                        contas_bancarias.numero_conta,
                        '-',
                        contas_bancarias.digito_conta),
                contas_bancarias.senha_bancaria_conta,
                contas_bancarias.senha_digital_conta
            FROM
                contas_bancarias
            WHERE
                contas_bancarias.nome_conta = %s
                    AND contas_bancarias.nome_proprietario_conta = %s
                    AND contas_bancarias.documento_proprietario_conta = %s;
            '''
            result_list = QueryExecutor().complex_consult_query(
                query=account_details_query,
                params=(
                    selected_option,
                    logged_user_name,
                    logged_user_document
                )
            )
            result_list = QueryExecutor().treat_complex_result(
                values_to_treat=result_list,
                values_to_remove=to_remove_list
            )
            if confirm_password_selection and consult_button:
                is_password_valid, hashed_password = (
                    Login().check_login(logged_user, safe_password)
                )
                if (
                    safe_password != ""
                    and confirm_safe_password != ""
                    and safe_password == confirm_safe_password
                    and is_password_valid
                ):
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)
                        st.subheader(
                            body="""
                            :white_check_mark: Dados da Consulta
                            """
                        )
                        with st.expander(label="Dados", expanded=True):
                            aux_string = ''
                            for i in range(0, len(result_list)):
                                st.write(bank_account_field_names[i])
                                aux_string = str(result_list[i])
                                aux_string = aux_string.replace('"', '')
                                if aux_string.startswith('b'):
                                    aux_string = aux_string[1:]
                                st.code(body="{}".format(aux_string))
                            log_query = '''
                            INSERT INTO
                                logs_atividades (
                                    usuario_log,
                                    tipo_log,
                                    conteudo_log
                                )
                            VALUES (%s, %s, %s);
                            '''
                            query_values = (
                                logged_user,
                                'Consulta',
                                '''
                                Consultou a conta bancária {}.
                                '''.format(selected_option)
                            )
                            QueryExecutor().insert_query(
                                query=log_query,
                                values=query_values,
                                success_message='Log gravado.',
                                error_message='Erro ao gravar log:'
                            )
                elif (
                        safe_password != ""
                        and confirm_safe_password != ""
                        and safe_password == confirm_safe_password
                        and is_password_valid is False
                ):
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        st.subheader(
                            body=":white_check_mark: Validação da Consulta"
                        )
                        with st.expander(
                            label="Validação dos dados",
                            expanded=True
                        ):
                            st.error(body="A senha informada é inválida.")
                elif (
                        safe_password != ""
                        and confirm_safe_password != ""
                        and safe_password != confirm_safe_password
                ):
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        st.subheader(body="""
                        :white_check_mark: Validação da Consulta
                        """
                                     )
                        with st.expander(
                            label="Validação dos dados",
                            expanded=True
                        ):
                            st.error(
                                body="As senhas informadas não coincidem."
                            )

            elif confirm_password_selection is False and consult_button:
                with col2:
                    st.subheader(body=":computer: Validação da Consulta")
                    st.warning(body="Confirme a seleção da conta.")

    def update_bank_account(self):
        """
        Função para a atualização de uma conta bancária.
        """
        logged_user_name, logged_user_document = Login().get_user_data(
            return_option="user_doc_name"
        )
        logged_user, logged_user_password = Login().get_user_data(
            return_option="user_login_password"
        )
        user_accounts_quantity = self.get_user_accounts_quantity()
        if user_accounts_quantity == 0:
            col1, col2, col3 = st.columns(3)
            with col2:
                st.warning(body="Você ainda não possui contas cadastradas.")
        elif user_accounts_quantity >= 1:
            col1, col2 = st.columns(2)
            user_bank_accounts = self.get_user_bank_accounts()
            with col1:
                st.subheader(body=":computer: Entrada de Dados")
                with st.expander(label="Dados", expanded=True):
                    selected_option = st.selectbox(
                        label="Selecione a conta",
                        options=user_bank_accounts
                    )
                    safe_password = st.text_input(
                        label="Informe sua senha",
                        type="password",
                        help="Corresponde a senha de acesso."
                    )
                    confirm_safe_password = st.text_input(
                        label="Confirme sua senha",
                        type="password",
                        help="Deve ser idêntica a senha informada acima."
                    )
                    confirm_selection = st.checkbox(label="Confirmar seleção")

            account_details_query = '''
            SELECT
                CONCAT('Conta: ',
                        contas_bancarias.nome_conta,
                        ' - Instituição: ',
                        contas_bancarias.instituicao_financeira),
                contas_bancarias.agencia,
                CONCAT('',
                        contas_bancarias.numero_conta,
                        '-',
                        contas_bancarias.digito_conta),
                contas_bancarias.senha_bancaria_conta,
                contas_bancarias.senha_digital_conta
            FROM
                contas_bancarias
            WHERE
                contas_bancarias.nome_conta = %s
                    AND contas_bancarias.nome_proprietario_conta = %s
                    AND contas_bancarias.documento_proprietario_conta = %s;'''

            result_list = QueryExecutor().complex_consult_query(
                query=account_details_query,
                params=(
                    selected_option,
                    logged_user_name,
                    logged_user_document
                )
            )
            result_list = QueryExecutor().treat_complex_result(
                values_to_treat=result_list,
                values_to_remove=to_remove_list
            )
            if confirm_selection:
                is_password_valid, hashed_password = Login().check_login(
                    logged_user,
                    safe_password
                )
                if (
                    safe_password != ""
                    and confirm_safe_password != ""
                    and safe_password == confirm_safe_password
                    and is_password_valid
                ):
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        st.subheader(
                            body="""
                            :white_check_mark: Validação dos Dados
                            """
                        )
                        with st.expander(label="Novos Dados", expanded=True):
                            aux_string = ''
                            for i in range(0, 3):
                                st.write(bank_account_field_names[i])
                                aux_string = str(result_list[i])
                                aux_string = aux_string.replace('"', '')
                                if aux_string.startswith('b'):
                                    aux_string = aux_string[1:]
                                st.code(body="{}".format(aux_string))
                            account_password = st.text_input(
                                label="Senha da conta",
                                max_chars=30,
                                type='password',
                                help='''
                                Senha utilizada para saques e demais
                                operações em terminais físicos.
                                '''
                            )
                            digital_account_password = st.text_input(
                                label="Senha digital da conta",
                                max_chars=30,
                                type='password',
                                help='''
                                Senha digital da conta,
                                utilizada para operações virtuais como Pix.
                                '''
                            )
                            confirm_new_bank_account_data = st.checkbox(
                                label="Confirmar novos dados"
                            )
                        update_bank_account_button = st.button(
                            label="""
                            :arrows_counterclockwise: Atualizar dados da conta
                            """
                        )
                    if (
                        confirm_new_bank_account_data
                        and update_bank_account_button
                        and account_password != ""
                        and digital_account_password != ""
                    ):
                        with col1:
                            with st.spinner(text="Aguarde..."):
                                sleep(2.5)
                        update_account_query = '''
                        UPDATE
                            contas_bancarias
                        SET
                            senha_bancaria_conta = %s,
                            senha_digital_conta = %s
                        WHERE
                            nome_conta = %s
                            AND
                                nome_proprietario_conta = %s
                            AND
                                documento_proprietario_conta = %s;
                        '''
                        update_account_values = (
                            account_password,
                            digital_account_password,
                            selected_option,
                            logged_user_name,
                            logged_user_document
                        )
                        QueryExecutor().insert_query(
                            query=update_account_query,
                            values=update_account_values,
                            success_message="Conta atualizada com sucesso!",
                            error_message="Erro ao atualizar conta:"
                        )
                        log_query = '''
                        INSERT INTO
                            logs_atividades (
                                usuario_log,
                                tipo_log,
                                conteudo_log
                            )
                        VALUES (%s, %s, %s);
                        '''
                        query_values = (
                            logged_user,
                            'Atualização',
                            '''
                            Atualizou a conta bancária {}
                            '''.format(selected_option)
                        )
                        QueryExecutor().insert_query(
                            query=log_query,
                            values=query_values,
                            success_message='Log gravado.',
                            error_message='Erro ao gravar log:'
                        )
                    elif (
                            confirm_new_bank_account_data is False
                            and update_bank_account_button
                            and account_password != ""
                            and digital_account_password != ""
                    ):
                        with col2:
                            st.subheader(
                                body="""
                                :white_check_mark: Validação dos Dados
                                """
                            )
                            with st.expander(
                                label="Validação dos dados",
                                expanded=True
                            ):
                                st.warning(
                                    body="Confirme os novos dados da conta."
                                )
                elif (
                        safe_password != ""
                        and confirm_safe_password != ""
                        and safe_password == confirm_safe_password
                        and is_password_valid is False
                ):
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        st.subheader(
                            body="""
                                :white_check_mark: Validação dos Dados
                                """
                        )
                        with st.expander(
                            label="Validação dos dados",
                            expanded=True
                        ):
                            st.error(body="A senha informada é inválida.")
                elif safe_password != confirm_safe_password:
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        st.subheader(
                            body="""
                                :white_check_mark: Validação dos Dados
                                """
                        )
                        with st.expander(
                            label="Validação dos dados",
                            expanded=True
                        ):
                            st.error(
                                body="As senhas informadas não coincidem."
                            )

    def delete_bank_account(self):
        """
        Função para a exclusão de uma conta bancária.
        """
        logged_user_name, logged_user_document = Login(
        ).get_user_data(return_option="user_doc_name")
        logged_user, logged_user_password = Login().get_user_data(
            return_option="user_login_password")
        user_accounts_quantity = self.get_user_accounts_quantity()
        if user_accounts_quantity == 0:
            col1, col2, col3 = st.columns(3)
            with col2:
                st.warning(body="Você ainda não possui contas cadastradas.")
        elif user_accounts_quantity >= 1:
            col1, col2 = st.columns(2)
            user_bank_accounts = self.get_user_bank_accounts()
            with col1:
                st.subheader(body=":computer: Entrada de Dados")
                with st.expander(label="Dados", expanded=True):
                    selected_option = st.selectbox(
                        label="Selecione a conta",
                        options=user_bank_accounts
                    )
                    safe_password = st.text_input(
                        label="Informe sua senha",
                        type="password",
                        help="Corresponde a senha de acesso."
                    )
                    confirm_safe_password = st.text_input(
                        label="Confirme sua senha",
                        type="password",
                        help="Deve ser idêntica a senha informada acima."
                    )
                    confirm_password_selection = st.checkbox(
                        label="Confirmar seleção"
                    )
            account_details_query = '''
            SELECT
                CONCAT('Conta: ',
                        contas_bancarias.nome_conta,
                        ' - Instituição: ',
                        contas_bancarias.instituicao_financeira),
                contas_bancarias.agencia,
                CONCAT('',
                        contas_bancarias.numero_conta,
                        '-',
                        contas_bancarias.digito_conta),
                contas_bancarias.senha_bancaria_conta,
                contas_bancarias.senha_digital_conta
            FROM
                contas_bancarias
            WHERE
                contas_bancarias.nome_conta = %s
                    AND contas_bancarias.nome_proprietario_conta = %s
                    AND contas_bancarias.documento_proprietario_conta = %s;
            '''
            result_list = QueryExecutor().complex_consult_query(
                query=account_details_query,
                params=(
                    selected_option,
                    logged_user_name,
                    logged_user_document
                )
            )
            result_list = QueryExecutor().treat_complex_result(
                values_to_treat=result_list,
                values_to_remove=to_remove_list
            )
            if confirm_password_selection:
                is_password_valid, hashed_password = Login().check_login(
                    logged_user,
                    safe_password
                )
                if (
                    safe_password != ""
                    and confirm_safe_password != ""
                    and safe_password == confirm_safe_password
                    and is_password_valid
                ):
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        st.subheader(
                            body="""
                                    :white_check_mark: Validação da Exclusão
                                    """
                        )
                        with st.expander(label="Dados", expanded=True):
                            aux_string = ''
                            for i in range(0, len(result_list)):
                                st.write(bank_account_field_names[i])
                                aux_string = str(result_list[i])
                                aux_string = aux_string.replace('"', '')
                                if aux_string.startswith('b'):
                                    aux_string = aux_string[1:]
                                st.code(body="{}".format(aux_string))
                            confirm_account_deletion = st.checkbox(
                                label="Confirmar exclusão da conta"
                            )
                        delete_account_button = st.button(
                            label=":wastebasket: Deletar conta"
                        )
                        if delete_account_button and confirm_account_deletion:
                            with col2:
                                with st.spinner(text="Aguarde..."):
                                    sleep(2.5)
                                delete_account_query = '''
                                DELETE
                                    contas_bancarias
                                FROM
                                    contas_bancarias
                                WHERE
                                    nome_conta = %s
                                    AND
                                        nome_proprietario_conta = %s
                                    AND
                                        documento_proprietario_conta = %s;
                                '''
                                delete_account_values = (
                                    selected_option,
                                    logged_user_name,
                                    logged_user_document
                                )
                                QueryExecutor().insert_query(
                                    query=delete_account_query,
                                    values=delete_account_values,
                                    success_message="Conta excluída.",
                                    error_message="Erro ao excluir conta:"
                                )
                                log_query = '''
                                INSERT INTO
                                    logs_atividades (
                                        usuario_log,
                                        tipo_log,
                                        conteudo_log
                                    )
                                VALUES (%s, %s, %s);
                                '''
                                query_values = (
                                    logged_user,
                                    'Exclusão',
                                    '''
                                    Excluiu a conta bancária {}
                                    '''.format(selected_option)
                                )
                                QueryExecutor().insert_query(
                                    query=log_query,
                                    values=query_values,
                                    success_message='Log gravado.',
                                    error_message='Erro ao gravar log:'
                                )
                        elif (
                                delete_account_button
                                and confirm_account_deletion is False
                        ):
                            with col2:
                                st.subheader(
                                    body="""
                                    :white_check_mark: Validação da Exclusão
                                    """
                                )
                                with st.expander(
                                    label="Validação dos dados",
                                    expanded=True
                                ):
                                    st.warning(
                                        body="Confirme a exclusão da conta."
                                    )
                elif (
                        safe_password != ""
                        and confirm_safe_password != ""
                        and safe_password == confirm_safe_password
                        and is_password_valid is False
                ):
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        st.subheader(
                            body="""
                                    :white_check_mark: Validação da Exclusão
                                    """
                        )
                        with st.expander(
                            label="Validação dos dados",
                            expanded=True
                        ):
                            st.error(body="A senha informada é inválida.")
                elif safe_password != confirm_safe_password:
                    with col2:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        st.subheader(
                            body="""
                                    :white_check_mark: Validação da Exclusão
                                    """
                        )
                        with st.expander(
                            label="Validação dos dados",
                            expanded=True
                        ):
                            st.error(
                                body="As senhas informadas não coincidem."
                            )

    def main_menu(self):
        """
        Menu Principal.
        """
        col1, col2, col3 = st.columns(3)
        with col1:
            st.header(body=":bank: Contas Bancárias")
        with col2:
            menu_options = {
                "Cadastrar conta": self.create_new_bank_account,
                "Consultar conta": self.read_bank_accounts,
                "Atualizar conta": self.update_bank_account,
                "Deletar conta": self.delete_bank_account
            }
            selected_option = st.selectbox(
                label="Menu",
                options=menu_options.keys()
            )
            selected_function = menu_options[selected_option]

        st.divider()

        selected_function()

# Projeto Computação em Núvem - 2018/2
## Engenharia da Computação - Insper 6º Semestre
### Por Pedro de la Peña

### Requisitos
1.Utilizar uma máquina UNIX para realização do SSH (dá para fazer com putty em Windows mas não garanto que funciona)

2.Configurar a AWS Key e Secret Key utilizando o comando <i>aws configure</i>. Caso não tenha o aplicativo, instale-o com <i>sudo snap install aws-cli --classic</i>

### Como utilizar
Baixar o repositório e com as credenciais da Amazon já configuradas, rodar o script <i>instance_launcher.py</i>. Dentro do código, há variáveis <i>"ownerName", "keyPair", "secGroupName" e "loadBalancerTag"</i> que podem ser alteradas, caso o usuário deseje. Também é preciso ter um arquivo <i>id_rsa.pub</i> no diretório. </br>

Após rodar o arquivo, o usuário pode escolher quantas instâncias serão criadas. O número é sempre +1 em relação ao input do usuário, pois uma máquina load balancer também é criada.

Após o código terminar de rodar, o usuário deve esperar as instâncias terminarem de iniciar, e isso pode ser acompanhado no dashboard da AWS -> EC2 -> Instances. Lá o usuário deve procurar por uma instância com a tag "pedro_lb" por default, e deve realizar uma conexão SSH com esta máquina. 

Na máquina, o usuário deve configurar novamente as suas credenciais da Amazon, utilizando o mesmo comando anteriormente descrito. Com isto feito, o usuário deve ir até o diretório /projcloud e rodar o arquivo lb.py para ativar o monitoramento e gerenciamento de isntâncias. A partir deste ponto, caso uma instância pare de funcionar (timeout de 7 segundos), o código automaticamente deleta a instância e a substitui com uma nova. 

Por fim, a aplicação consiste em rodar localmente o arquivo <i>firebase_tasks.py</i>, contudo, antes deve alterar o endpoint do arquivo para o IP da máquina loadbalancer. O usuário pode então realizar o comando <i>"python3 firebase_tasks 'tarefa listar'"</i> para conseguir se conectar a uma das instancias disponíveis (aleatoriamente) e receber as informações do servidor Firebase conectado à cada uma delas (stateless).

### Bugs conhecidos
A aplicação do Firebase deveria permitir que o usuário conseguisse realizar um "tarefa adicionar 'arg1' 'arg2'", porém isso não está funcionando como o devido (migué do "get only" but using a Firebase database instead).

O loadbalancer precisa ficar aberto no terminal para funcionar.






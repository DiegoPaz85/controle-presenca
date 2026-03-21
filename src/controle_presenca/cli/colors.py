class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

def print_c(texto, cor=Colors.WHITE, estilo=''):
    print(f"{estilo}{cor}{texto}{Colors.RESET}")

def print_success(texto):
    print_c(f"✅ {texto}", Colors.GREEN)

def print_error(texto):
    print_c(f"❌ {texto}", Colors.RED)

def print_warning(texto):
    print_c(f"⚠️  {texto}", Colors.YELLOW)

def print_info(texto):
    print_c(f"ℹ️  {texto}", Colors.CYAN)

def print_header(texto):
    """Imprime cabeçalho formatado"""
    print_c("=" * 50, Colors.CYAN, Colors.BOLD)
    print_c(texto.center(50), Colors.CYAN, Colors.BOLD)
    print_c("=" * 50, Colors.CYAN, Colors.BOLD)

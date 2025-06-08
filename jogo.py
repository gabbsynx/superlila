import pygame
import sys
import random
pygame.mixer.init()

# Sons
som_pulo = pygame.mixer.Sound('som/pulo.mp3')
som_moeda = pygame.mixer.Sound('som/moeda.mp3')
som_trampolim = pygame.mixer.Sound('som/msctramolim.wav')
som_cenas = pygame.mixer.Sound('som/msccenas.mp3')



som_pulo.set_volume(0.1)    # Volume de 0.0 até 1.0
som_moeda.set_volume(0.1)
som_cenas.set_volume(0.1)

def gerar_moedas_sobre_plataformas(quantidade, plataformas):
    moedas = []
    for _ in range(quantidade):
        plataforma = random.choice(plataformas)
        x = plataforma.rect.centerx - 32  # Centraliza a moeda (- metade da largura da moeda)
        y = plataforma.rect.top - 65      # Um pouco acima, não tanto


        moedas.append(Moeda(x, y))
    return moedas

def gerar_estrelas_sobre_plataformas(quantidade, plataformas):
    estrelas = []
    for _ in range(quantidade):
        plataforma = random.choice(plataformas)
        x = plataforma.rect.centerx - 65  # Centraliza a moeda (- metade da largura da moeda)
        y = plataforma.rect.top - 65      # Um pouco acima, não tanto

        estrelas.append(Estrela(x, y))
    return estrelas

pygame.init()

largura =  1920 #1280
altura = 1030 #700
tela = pygame.display.set_mode((largura, altura), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("SUPER LILA")

relogio = pygame.time.Clock()
FPS = 60

GRAVIDADE = 1
FORCA_PULO = 21

class GameState:
    vidas_jogador = 3

    @classmethod
    def resetar_vidas(cls):
        cls.vidas_jogador = 3

    @classmethod
    def perder_vida(cls):
        cls.vidas_jogador -= 1
        return cls.vidas_jogador <= 0

# Base da estrutura de cenas
class Cena:
    def handle_events(self, eventos):
        pass

    def update(self):
        pass

    def draw(self, tela):
        pass

class Jogador():
    def __init__(self):
        try:
            self.image_direita = pygame.image.load("imagens/lilaLado.png").convert_alpha()
            self.image_direita = pygame.transform.scale(self.image_direita, (145, 150))
            self.image_esquerda = pygame.transform.flip(self.image_direita, True, False)
            self.image_atual = self.image_direita
            self.rect = self.image_atual.get_rect(topleft=(110, 60))
        except pygame.error as e:
            print(f"Erro ao carregar imagem do jogador: {e}")
            self.image_direita = pygame.Surface((145, 150)); self.image_direita.fill((255,0,0))
            self.image_esquerda = pygame.Surface((145, 150)); self.image_esquerda.fill((255,0,0))
            self.image_atual = self.image_direita
            self.rect = self.image_atual.get_rect(topleft=(110, 60))

        self.vel_y = 0
        self.vel_x = 0 
        self.no_chao = False
        self.vivo = True

        self.pontos = 0
        self.invencivel = False
        self.tempo_invencivel = 0

        try:
            self.coracao_img = pygame.image.load('imagens/coracao.png').convert_alpha()
            self.coracao_img = pygame.transform.scale(self.coracao_img, (75, 75))
        except pygame.error as e:
            print(f"Erro ao carregar imagem do coração: {e}")
            self.coracao_img = pygame.Surface((75,75)); self.coracao_img.fill((255,0,0))


    @property
    def vidas(self):
        return GameState.vidas_jogador

    @vidas.setter
    def vidas(self, valor):
        GameState.vidas_jogador = valor

    def perder_vida(self):
        morreu = GameState.perder_vida()
        if morreu:
            self.vivo = False
        return morreu


    def desenhar(self, tela):
        tela.blit(self.image_atual, self.rect.topleft)
        for i in range(GameState.vidas_jogador):
            x = 10 + i * 85
            y = 30
            tela.blit(self.coracao_img, (x, y))

    def aplicar_gravidade(self):
        self.vel_y += GRAVIDADE
        self.rect.y += self.vel_y

    def pular(self):
        if self.no_chao:
            self.vel_y = -FORCA_PULO
            self.no_chao = False
            som_pulo.play()

    def mover(self, teclas):
        movimento_x = 0 # Usar uma variável para acumular movimento
        if teclas[pygame.K_LEFT] and self.rect.left > 0:
            movimento_x = -7
            self.image_atual = self.image_esquerda
        if teclas[pygame.K_RIGHT]: # Limite direito pode ser verificado globalmente se necessário
            movimento_x = 7
            self.image_atual = self.image_direita
        if teclas[pygame.K_SPACE]:
            self.pular()
        
        self.rect.x += movimento_x # Aplicar movimento acumulado

    def checar_colisoes(self, plataformas, chao, trampolins=[], inimigos=[], inimigos2=[], inimigos3=[], inimigos4=[], fogos=[], estacas=[]):
        self.no_chao = False # Resetar no início de cada frame

        # --- CORREÇÃO: Checar colisões com chão e plataformas PRIMEIRO --- 
        # Isso ajusta a posição do jogador (self.rect.bottom) ANTES de checar perigos

        for plataforma in plataformas:
            if self.rect.colliderect(plataforma.rect):
                overlap_x = min(self.rect.right - plataforma.rect.left, plataforma.rect.right - self.rect.left)
                overlap_y = min(self.rect.bottom - plataforma.rect.top, plataforma.rect.bottom - self.rect.top)
                
                # Colisão Vertical (caindo ou batendo cabeça)
                if overlap_y < overlap_x:
                    # Caindo na plataforma
                    if self.vel_y > 0 and self.rect.centery < plataforma.rect.centery: # Adicionado verificação de centery para robustez
                        self.rect.bottom = plataforma.rect.top
                        self.vel_y = 0
                        self.no_chao = True
                    # Batendo a cabeça na plataforma
                    elif self.vel_y < 0 and self.rect.centery > plataforma.rect.centery: # Adicionado verificação de centery
                        self.rect.top = plataforma.rect.bottom
                        self.vel_y = 0
                # Colisão Horizontal com plataforma (empurrar para o lado)
                else:
                    if self.rect.centerx < plataforma.rect.centerx:
                        self.rect.right = plataforma.rect.left
                    else:
                        self.rect.left = plataforma.rect.right

        # Colisão com o chão principal
        if self.rect.colliderect(chao.rect) and self.vel_y >= 0:
            self.rect.bottom = chao.rect.top
            self.vel_y = 0
            self.no_chao = True
            
        # Colisão com trampolins (pode ficar aqui ou junto com plataformas)
        for trampolim in trampolins:
            if self.rect.colliderect(trampolim.rect):
                # Apenas ativa se estiver caindo sobre ele
                if self.vel_y > 0 and self.rect.bottom <= trampolim.rect.top + abs(self.vel_y): # Checa se estava acima no frame anterior
                    self.rect.bottom = trampolim.rect.top
                    self.vel_y = -trampolim.forca_trampolim
                    self.no_chao = False # Está no ar após trampolim
                    som_trampolim.play() # Adicione som se tiver

        # --- FIM DA CORREÇÃO DE ORDEM ---

        # Checar invencibilidade
        if self.invencivel and pygame.time.get_ticks() - self.tempo_invencivel > 1000: # 1 segundo
            self.invencivel = False

        # --- Checar colisões com PERIGOS (Fogo, Estacas) DEPOIS de ajustar posição --- 
        for fogo in fogos:
            if self.rect.colliderect(fogo.rect):
                # Verifica colisão real, agora que a posição Y deve estar correta
                # A condição original `self.rect.bottom >= fogo.rect.top - 10` pode ser muito permissiva
                # Uma colisão simples pode ser suficiente agora, ou uma pequena margem:
                if self.rect.bottom > fogo.rect.top + 5: # Pequena margem para evitar colisões falsas
                    print(f"DEBUG (Após correção): rect.bottom = {self.rect.bottom}, fogo.top = {fogo.rect.top}")
                    print("Você caiu no fogo!")
                    self.vivo = False
                    return # Sai imediatamente ao morrer
                    
        for estaca in estacas:
            if self.rect.colliderect(estaca.rect):
                 # Adicionar uma verificação para garantir que o jogador está caindo na estaca
                 if self.vel_y > 0 and self.rect.bottom > estaca.rect.top:
                    print("MORTE! Você foi espetado por uma estaca!")
                    self.vivo = False # Morte direta
                    return

        # --- Checar colisões com INIMIGOS --- (Lógica original mantida, mas agora após ajuste de posição)
        for inimigo in inimigos[:]:
            if self.rect.colliderect(inimigo.rect):
                centro_jogador_x = self.rect.centerx
                centro_inimigo_x = inimigo.rect.centerx
                centro_jogador_y = self.rect.centery
                centro_inimigo_y = inimigo.rect.centery
                overlap_x = min(self.rect.right - inimigo.rect.left, inimigo.rect.right - self.rect.left)
                overlap_y = min(self.rect.bottom - inimigo.rect.top, inimigo.rect.bottom - self.rect.top)

                if overlap_y < overlap_x: # Colisão vertical
                    if centro_jogador_y < centro_inimigo_y and self.vel_y > 0: # Caindo sobre o inimigo
                        self.rect.bottom = inimigo.rect.top
                        self.vel_y = -FORCA_PULO // 2 # Quicar
                        inimigos.remove(inimigo)
                        self.no_chao = True # Considera "chão" momentaneamente
                    elif centro_jogador_y > centro_inimigo_y and not self.invencivel: # Batendo cabeça
                        self.rect.top = inimigo.rect.bottom
                        self.vel_y = 0
                        if self.perder_vida(): return
                        self.invencivel = True
                        self.tempo_invencivel = pygame.time.get_ticks()
                elif not self.invencivel: # Colisão horizontal
                    if self.perder_vida(): return
                    self.invencivel = True
                    self.tempo_invencivel = pygame.time.get_ticks()
                    # Empurrar jogador um pouco para trás
                    if centro_jogador_x < centro_inimigo_x: self.rect.right = inimigo.rect.left
                    else: self.rect.left = inimigo.rect.right
            if not self.vivo: return

        for inimigo2 in inimigos2[:]:
            if self.rect.colliderect(inimigo2.rect):
                centro_jogador_x = self.rect.centerx
                centro_inimigo2_x = inimigo2.rect.centerx
                centro_jogador_y = self.rect.centery
                centro_inimigo2_y = inimigo2.rect.centery
                overlap_x = min(self.rect.right - inimigo2.rect.left, inimigo2.rect.right - self.rect.left)
                overlap_y = min(self.rect.bottom - inimigo2.rect.top, inimigo2.rect.bottom - self.rect.top)

                if overlap_y < overlap_x: # Colisão vertical
                    if centro_jogador_y < centro_inimigo2_y and self.vel_y > 0: # Caindo sobre
                        self.rect.bottom = inimigo2.rect.top
                        self.vel_y = -FORCA_PULO // 2
                        self.no_chao = True
                        if inimigo2.receber_dano():
                            inimigos2.remove(inimigo2)
                    elif centro_jogador_y > centro_inimigo2_y and not self.invencivel: # Batendo cabeça
                        self.rect.top = inimigo2.rect.bottom
                        self.vel_y = 0
                        if self.perder_vida(): return
                        self.invencivel = True
                        self.tempo_invencivel = pygame.time.get_ticks()
                elif not self.invencivel: # Colisão horizontal
                    if self.perder_vida(): return
                    self.invencivel = True
                    self.tempo_invencivel = pygame.time.get_ticks()
                    if centro_jogador_x < centro_inimigo2_x: self.rect.right = inimigo2.rect.left
                    else: self.rect.left = inimigo2.rect.right
            if not self.vivo: return
            
        for inimigo3 in inimigos3[:]: # Mesma lógica do inimigo normal
            if self.rect.colliderect(inimigo3.rect):
                centro_jogador_x = self.rect.centerx
                centro_inimigo_x = inimigo3.rect.centerx # Corrigido para inimigo3
                centro_jogador_y = self.rect.centery
                centro_inimigo_y = inimigo3.rect.centery # Corrigido para inimigo3
                overlap_x = min(self.rect.right - inimigo3.rect.left, inimigo3.rect.right - self.rect.left)
                overlap_y = min(self.rect.bottom - inimigo3.rect.top, inimigo3.rect.bottom - self.rect.top)

                if overlap_y < overlap_x:
                    if centro_jogador_y < centro_inimigo_y and self.vel_y > 0:
                        self.rect.bottom = inimigo3.rect.top
                        self.vel_y = -FORCA_PULO // 2
                        inimigos3.remove(inimigo3)
                        self.no_chao = True
                    elif centro_jogador_y > centro_inimigo_y and not self.invencivel:
                        self.rect.top = inimigo3.rect.bottom
                        self.vel_y = 0
                        if self.perder_vida(): return
                        self.invencivel = True
                        self.tempo_invencivel = pygame.time.get_ticks()
                elif not self.invencivel:
                    if self.perder_vida(): return
                    self.invencivel = True
                    self.tempo_invencivel = pygame.time.get_ticks()
                    if centro_jogador_x < centro_inimigo_x: self.rect.right = inimigo3.rect.left
                    else: self.rect.left = inimigo3.rect.right
            if not self.vivo: return

        for inimigo4 in inimigos4[:]:
            if self.rect.colliderect(inimigo4.rect) and not self.invencivel:
                if self.perder_vida(): return
                self.invencivel = True
                self.tempo_invencivel = pygame.time.get_ticks()
                # Empurrar um pouco
                if self.rect.centerx < inimigo4.rect.centerx: self.rect.x -= 10
                else: self.rect.x += 10
            if not self.vivo: return

        # Verificar se caiu para fora da tela (exemplo simples, ajustar limites)
        # Esta verificação deve vir por último, após todas as colisões terem sido resolvidas
        if self.rect.top > altura: # 'altura' deve ser definida globalmente ou passada como parâmetro
            print("Caiu fora da tela!")
            self.vivo = False 

    # Método atualizar_invencibilidade não é mais necessário separadamente
    # def atualizar_invencibilidade(self):
    #     if self.invencivel:
    #         tempo_atual = pygame.time.get_ticks()
    #         if tempo_atual - self.tempo_invencivel > 1000:
    #             self.invencivel = False



class Inimigo:
    def __init__(self, x, y):
        try:
            self.image_original = pygame.image.load("imagens2/inimigo1.png").convert_alpha()
            self.image = pygame.transform.scale(self.image_original, (70, 70))
        except pygame.error as e:
            print(f"Erro ao carregar imagem Inimigo1: {e}")
            self.image = pygame.Surface((70,70)); self.image.fill((128,0,128)) # Roxo
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidade = 2
        self.direcao = 1
        self.limite_esquerda = x - 150
        self.limite_direita = x + 150

    def update(self, plataformas, chao=None): # chao é opcional
        self.rect.x += self.velocidade * self.direcao
        if self.rect.left <= self.limite_esquerda:
            self.direcao = 1
            self.rect.left = self.limite_esquerda
        elif self.rect.right >= self.limite_direita:
            self.direcao = -1
            self.rect.right = self.limite_direita
        # Se o inimigo precisar interagir com a gravidade ou plataformas, adicione aqui.
        # Por ora, ele se move em Y fixo ou usa 'chao' para se alinhar se fornecido.
        if chao: # Mantém o inimigo no topo do objeto 'chao' se ele for fornecido
            # Esta lógica assume que o Inimigo deve ficar no "chão principal"
            # Se ele deve ficar em plataformas específicas, a lógica precisa ser mais complexa
            # e provavelmente integrada à sua posição Y inicial.
            # Para este tipo de inimigo que patrulha, geralmente a altura Y é fixa.
            # self.rect.bottom = chao.rect.top # Comentado, pois geralmente y é fixo.
            pass


    def desenhar(self, tela):
        tela.blit(self.image, self.rect.topleft)

class Inimigo2:
    def __init__(self, x, y):
        try:
            self.image_original = pygame.image.load("imagens2/inimigos2.png").convert_alpha()
            self.image_normal = pygame.transform.scale(self.image_original, (100, 100))
        except pygame.error as e:
            print(f"Erro ao carregar imagem Inimigo2: {e}")
            self.image_normal = pygame.Surface((100,100)); self.image_normal.fill((0,100,0)) # Verde escuro
        
        self.image_danificado = self.image_normal.copy()
        overlay = pygame.Surface((100, 100), pygame.SRCALPHA) # SRCALPHA para transparência
        overlay.fill((255, 0, 0, 80)) # Vermelho com alpha
        self.image_danificado.blit(overlay, (0, 0))

        self.rect = self.image_normal.get_rect(topleft=(x, y))
        self.velocidade = 2
        self.direcao = 1
        self.posicao_inicial_x = x
        self.distancia_movimento = 130
        self.vidas = 2
        self.max_vidas = 2
        self.tempo_invencivel_inimigo = 0 # Renomeado para evitar conflito com jogador
        self.duracao_invencibilidade_inimigo = 500 # Renomeado
        self.image = self.image_normal # Imagem inicial
        self.atualizar_aparencia()


    def atualizar_aparencia(self):
        if self.vidas == self.max_vidas:
            self.image = self.image_normal
        else:
            self.image = self.image_danificado

    def receber_dano(self):
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - self.tempo_invencivel_inimigo > self.duracao_invencibilidade_inimigo:
            self.vidas -= 1
            self.tempo_invencivel_inimigo = tempo_atual
            self.atualizar_aparencia()
            if self.vidas <= 0:
                return True
            else:
                print(f"Inimigo2 levou dano! Vidas restantes: {self.vidas}")
                return False
        return False

    def update(self, plataformas): # Não usa chao
        self.rect.x += self.velocidade * self.direcao
        limite_esquerda = self.posicao_inicial_x - self.distancia_movimento
        limite_direita = self.posicao_inicial_x + self.distancia_movimento
        if self.rect.x <= limite_esquerda:
            self.direcao = 1
            self.rect.x = limite_esquerda
        elif self.rect.x >= limite_direita:
            self.direcao = -1
            self.rect.x = limite_direita

    def desenhar(self, tela):
        tempo_atual = pygame.time.get_ticks()
        # Piscar se danificado e invencível
        if self.vidas < self.max_vidas and tempo_atual - self.tempo_invencivel_inimigo < self.duracao_invencibilidade_inimigo:
            if (tempo_atual // 100) % 2: # Pisca a cada 100ms
                tela.blit(self.image, self.rect.topleft)
        else:
            tela.blit(self.image, self.rect.topleft)


class Inimigo3:
    def __init__(self, x, y):
        try:
            self.image_original = pygame.image.load("imagens2/inimigo3.png").convert_alpha()
            self.image = pygame.transform.scale(self.image_original, (80, 80))
        except pygame.error as e:
            print(f"Erro ao carregar imagem Inimigo3: {e}")
            self.image = pygame.Surface((80,80)); self.image.fill((255,165,0)) # Laranja
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidade = 1
        self.direcao = 1
        self.limite_esquerda = x - 100
        self.limite_direita = x + 100

    def update(self, plataformas):
        self.rect.x += self.velocidade * self.direcao
        if self.rect.left <= self.limite_esquerda or self.rect.right >= self.limite_direita:
            self.direcao *= -1

    def desenhar(self, tela):
        tela.blit(self.image, self.rect.topleft)

class Inimigo4:
    def __init__(self, x, y):
        try:
            self.image_original = pygame.image.load("imagens2/inimigo4.png").convert_alpha()
            self.image = pygame.transform.scale(self.image_original, (80, 80))
        except pygame.error as e:
            print(f"Erro ao carregar imagem Inimigo4: {e}")
            self.image = pygame.Surface((90,90)); self.image.fill((100,100,100)) # Cinza
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidade = 1.5
        self.direcao = 1
        self.limite_esquerda = x - 800
        self.limite_direita = x + 800

    def update(self):
        self.rect.x += self.velocidade * self.direcao
        if self.rect.left <= self.limite_esquerda or self.rect.right >= self.limite_direita:
            self.direcao *= -1

    def desenhar(self, tela):
        tela.blit(self.image, self.rect.topleft)

class Chao:
    def __init__(self):
        altura_chao = 20
        y_chao = altura - altura_chao
        self.rect = pygame.Rect(0, y_chao, largura, altura_chao)

    def desenhar(self, tela):
        # pygame.draw.rect(tela, (0,0,0), self.rect) # Opcional: desenhar o chao se for visível
        pass


class Plataforma:
    def __init__(self, x, y):
        try:
            self.image = pygame.image.load("imagens/bloco.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (89, 89))
        except pygame.error as e:
            print(f"Erro ao carregar imagem da plataforma: {e}")
            self.image = pygame.Surface((89,89)); self.image.fill((139,69,19)) # Marrom
        self.rect = self.image.get_rect(topleft=(x, y))

    def desenhar(self, tela):
        tela.blit(self.image, self.rect.topleft)

class Estaca:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y+50, 90, 40) # Ajustado para imagem 90x90, colisão na base
        try:
            self.image = pygame.image.load("imagens2/estacavirada.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (90, 90))
        except pygame.error as e:
            print(f"Erro ao carregar imagem da estaca: {e}")
            self.image = None # Usará o desenho do polígono
            self.rect = pygame.Rect(x, y, 30, 40) # Retorna para o rect original se imagem falhar

    def desenhar(self, tela):
        if self.image:
            tela.blit(self.image, (self.rect.x, self.rect.y - 50)) # Desenha a imagem completa
            # pygame.draw.rect(tela, (255,0,0), self.rect, 1) # Hitbox para debug
        else:
            # Desenha triângulo pontudo vermelho se imagem falhar
            pontos = [
                (self.rect.centerx, self.rect.top),      # Ponta
                (self.rect.left, self.rect.bottom),      # Base esquerda
                (self.rect.right, self.rect.bottom)      # Base direita
            ]
            pygame.draw.polygon(tela, (200, 0, 0), pontos)


class Moeda:
    def __init__(self, x, y):
        try:
            self.image = pygame.image.load('imagens/moeda.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (65, 65))
        except pygame.error as e:
            print(f"Erro ao carregar imagem da moeda: {e}")
            self.image = pygame.Surface((65,65)); self.image.fill((255,215,0)) # Dourado
        self.rect = self.image.get_rect(topleft=(x, y))

    def desenhar(self, tela):
        tela.blit(self.image, self.rect.topleft)

class Estrela:
    def __init__(self, x, y):
        try:
            self.image = pygame.image.load('imagens/estrela.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (65, 65))
        except pygame.error as e:
            print(f"Erro ao carregar imagem da estrela: {e}")
            self.image = pygame.Surface((65,65)); self.image.fill((255,255,0)) # Amarelo
        self.rect = self.image.get_rect(topleft=(x, y))

    def desenhar(self, tela):
        tela.blit(self.image, self.rect.topleft)

class Trampolim:
    def __init__(self, x, y, tamanho=50):  # ✅ tamanho opcional
        super().__init__()
        self.rect = pygame.Rect(x, y, tamanho, 20)  # ou o que quiser
        try:
            self.image = pygame.image.load("imagens/trampolim.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 45))
        except pygame.error as e:
            print(f"Erro ao carregar imagem do trampolim: {e}")
            self.image = pygame.Surface((50,45)); self.image.fill((0,0,255)) # Azul
        self.rect = self.image.get_rect(topleft=(x, y))
        self.forca_trampolim = 30

    def desenhar(self, tela):
        tela.blit(self.image, self.rect.topleft)


class Fogo:
    def __init__(self, x, y, largura_fogo=100, altura_fogo=30):
        try:
            self.image = pygame.image.load("imagens/fogo.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (largura_fogo, altura_fogo))
        except pygame.error as e:
            print(f"Erro ao carregar imagem do fogo: {e}")
            self.image = pygame.Surface((largura_fogo, altura_fogo))
            self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(topleft=(x,y))

    def update(self):
        pass

    def desenhar(self, tela):
        tela.blit(self.image, self.rect.topleft)

class CenaInicial(Cena):
    def __init__(self, jogador):
        pygame.mixer.music.load('som\somInicio.mp3')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

        self.jogador = jogador
        try:
            self.imagem = pygame.image.load("imagens/inicial.png")
            self.imagem = pygame.transform.scale(self.imagem, (largura, altura))
        except pygame.error as e:
            print(f"Erro fatal ao carregar imagem inicial: {e}")
            self.imagem = pygame.Surface((largura, altura))
            self.imagem.fill((0,0,0)) # Fundo preto
            fonte_erro = pygame.font.Font(None, 50)
            texto_erro = fonte_erro.render("Erro: 'imagens/inicial.png' nao encontrada.", True, (255, 0, 0))
            rect_erro = texto_erro.get_rect(center=(largura // 2, altura // 2))
            self.imagem.blit(texto_erro, rect_erro)
            # pygame.quit() # Pode sair se a imagem inicial for crucial e não puder ser substituída
            # sys.exit()

        self.botao_rect = pygame.Rect(750, 645, 400, 70)
        self.botao_sair = pygame.Rect(largura - 250, 25, 250, 40)

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.botao_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()  #  Para a música da tela inicial
                    return CenaUM  (self.jogador)

                elif self.botao_sair.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        return None

    def update(self):
        return None

    def draw(self, tela):
        tela.blit(self.imagem, (0, 0))
        # Opcional: desenhar retângulos nos botões para debug
        #pygame.draw.rect(tela, (200, 200, 200), self.botao_rect, 2)
        #pygame.draw.rect(tela, (200, 0, 0), self.botao_sair, 2)


class CenaUM(Cena):
    def __init__(self, jogador_existente):
        pygame.mixer.music.load('som/msccenas.mp3')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

        self.jogador = jogador_existente
        self.jogador.rect.topleft = (40, 500)
        self.jogador.vel_y = 0
        self.jogador.no_chao = True 

        try:
            self.fundo = pygame.image.load('imagens/tela1.png')
            self.fundo = pygame.transform.scale(self.fundo, [largura, altura])
            self.coracao_img = pygame.image.load('imagens/coracao.png').convert_alpha()
            self.coracao_img = pygame.transform.scale(self.coracao_img, (75, 75))
        except pygame.error as e:
            print(f"Erro ao carregar imagens para CenaUM: {e}")
            # Fallback para fundo e coração
            self.fundo = pygame.Surface((largura, altura)); self.fundo.fill((100,100,200))
            self.coracao_img = pygame.Surface((75,75)); self.coracao_img.fill((255,0,0))


        self.chao = Chao()
        self.plataformas = [
            Plataforma(508, 810), Plataforma(596, 810), Plataforma(685, 810), Plataforma(770, 810),
            Plataforma(1000, 600), Plataforma(922, 600),
            Plataforma(1299, 740), Plataforma(1220, 740), Plataforma(1387, 740), Plataforma(1476, 740),
        ]
        self.moedas = [Moeda(500, 650), Moeda(700, 500), Moeda(1100, 450)]
        self.estrelas = [Estrela(985, 340), Estrela(1290, 500), Estrela(1500, 600)]
        self.inimigos = [Inimigo(250, self.chao.rect.top - 70)] # Ajusta Y do inimigo para o chao
        self.inimigos3 = [Inimigo3(1387, 740 - 80)] # Ajusta Y do inimigo para plataforma

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                
                pygame.quit()
                sys.exit()
        return None

    def update(self):
        teclas = pygame.key.get_pressed()
        self.jogador.mover(teclas)
        self.jogador.aplicar_gravidade()
        self.jogador.checar_colisoes(self.plataformas, self.chao, inimigos=self.inimigos, inimigos3=self.inimigos3)

        if not self.jogador.vivo:
            return GameOver(self.jogador, CenaUM)

        for inimigo in self.inimigos:
            inimigo.update(self.plataformas, self.chao)
        for inimigo3 in self.inimigos3:
            inimigo3.update(self.plataformas)

        for moeda in self.moedas[:]:
            if self.jogador.rect.colliderect(moeda.rect):
                som_moeda.play()
                self.moedas.remove(moeda)
                self.jogador.pontos += 50
        for estrela in self.estrelas[:]:
            if self.jogador.rect.colliderect(estrela.rect):
                self.estrelas.remove(estrela)
                self.jogador.pontos += 100

        if self.jogador.rect.left >= largura: # Transição por sair pela direita
            return CenaDOIS(self.jogador)
        return None

    def draw(self, tela):
        tela.blit(self.fundo, (0, 0))
        self.chao.desenhar(tela)
        for p in self.plataformas: p.desenhar(tela)
        for i in self.inimigos: i.desenhar(tela)
        for i3 in self.inimigos3: i3.desenhar(tela)
        for m in self.moedas: m.desenhar(tela)
        for e in self.estrelas: e.desenhar(tela)
        self.jogador.desenhar(tela)
        # Vidas já são desenhadas pelo jogador.desenhar()

class CenaDOIS(Cena):
    def __init__(self, jogador_existente):
        self.jogador = jogador_existente
        self.jogador.rect.topleft = (50, 500)
        self.jogador.vel_y = 0
        self.jogador.no_chao = False

        try:
            self.fundo = pygame.image.load('imagens/tela2.png')
            self.fundo = pygame.transform.scale(self.fundo, [largura, altura])
            self.coracao_img = pygame.image.load('imagens/coracao.png').convert_alpha() # Usado no draw do jogador
            self.coracao_img = pygame.transform.scale(self.coracao_img, (75, 75))
        except pygame.error as e:
            print(f"Erro ao carregar imagens para CenaDOIS: {e}")
            self.fundo = pygame.Surface((largura, altura)); self.fundo.fill((100,200,100))
            self.coracao_img = pygame.Surface((75,75)); self.coracao_img.fill((255,0,0))


        self.chao = Chao() # Adicionado para consistência
        self.plataformas = [
            Plataforma(650, 879), Plataforma(840, 760), Plataforma(980, 669),
            Plataforma(1150,550),
            Plataforma(1327, 669), Plataforma(1520, 760), Plataforma(1690, 879),
        ]
        self.moedas = [Moeda(790, 600), Moeda(970, 500), Moeda(1550, 600)]
        self.estrelas = [Estrela(1157, 420), Estrela(1350, 490)]
        self.inimigos = [Inimigo(400, self.chao.rect.top - 70)] # Ajusta Y

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        return None

    def update(self):
        teclas = pygame.key.get_pressed()
        self.jogador.mover(teclas)
        self.jogador.aplicar_gravidade()
        self.jogador.checar_colisoes(self.plataformas, self.chao, inimigos=self.inimigos)

        if not self.jogador.vivo:
            return GameOver(self.jogador, CenaDOIS)

        for inimigo in self.inimigos:
            inimigo.update(self.plataformas, self.chao)

        for moeda in self.moedas[:]:
            if self.jogador.rect.colliderect(moeda.rect):
                som_moeda.play()
                self.moedas.remove(moeda)
                self.jogador.pontos += 50
        for estrela in self.estrelas[:]:
            if self.jogador.rect.colliderect(estrela.rect):
                self.estrelas.remove(estrela)
                self.jogador.pontos += 100

        if self.jogador.rect.right >= largura - 10: # Condição de saída
            return CenaTRES(self.jogador)
        return None

    def draw(self, tela):
        tela.blit(self.fundo, (0, 0))
        self.chao.desenhar(tela)
        for p in self.plataformas: p.desenhar(tela)
        for i in self.inimigos: i.desenhar(tela)
        for m in self.moedas: m.desenhar(tela)
        for e in self.estrelas: e.desenhar(tela)
        self.jogador.desenhar(tela)


class CenaTRES(Cena):
    def __init__(self, jogador_existente):
        self.jogador = jogador_existente
        self.jogador.rect.topleft = (50, 500)
        self.jogador.vel_y = 0
        self.jogador.no_chao = False
        
        try:
            self.fundo = pygame.image.load('imagens/tela3.png')
            self.fundo = pygame.transform.scale(self.fundo, [largura, altura])
            self.coracao_img = pygame.image.load('imagens/coracao.png').convert_alpha()
            self.coracao_img = pygame.transform.scale(self.coracao_img, (75, 75))
        except pygame.error as e:
            print(f"Erro ao carregar imagens para CenaTRES: {e}")
            self.fundo = pygame.Surface((largura, altura)); self.fundo.fill((200,100,100))
            self.coracao_img = pygame.Surface((75,75)); self.coracao_img.fill((255,0,0))

        self.chao = Chao()
        self.plataformas = [
            Plataforma(185, 900), Plataforma(320, 500), Plataforma(7, 300),
            Plataforma(480, 200), Plataforma(760, 435), Plataforma(1055, 560),
            Plataforma(1170, 805), Plataforma(1170, 890), Plataforma(1250, 890),
            Plataforma(1505, 789), Plataforma(1580, 789), Plataforma(1669, 789),
            Plataforma(1756, 789), Plataforma(1840, 789),
        ]
        self.moedas = gerar_moedas_sobre_plataformas(5, self.plataformas)
        self.estrelas = gerar_estrelas_sobre_plataformas(2, self.plataformas)

        self.trampolins = [Trampolim(205, 900-45), Trampolim(342, 500-45)] # Ajusta Y do trampolim para plataforma
        self.inimigos = [Inimigo(1200, self.chao.rect.top - 70)]
        self.inimigos2 = [Inimigo2(615, self.chao.rect.top - 100)]
        self.estacas = [Estaca(1370, self.chao.rect.top - 90)] # Ajusta Y da estaca

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        return None

    def update(self):
        teclas = pygame.key.get_pressed()
        self.jogador.mover(teclas)
        self.jogador.aplicar_gravidade()
        self.jogador.checar_colisoes(
            self.plataformas, self.chao, trampolins=self.trampolins,
            inimigos=self.inimigos, inimigos2=self.inimigos2, estacas=self.estacas
        )

        if not self.jogador.vivo:
            return GameOver(self.jogador, CenaTRES)

        for i in self.inimigos: i.update(self.plataformas, self.chao)
        for i2 in self.inimigos2: i2.update(self.plataformas)

        for m in self.moedas[:]:
            if self.jogador.rect.colliderect(m.rect):
                som_moeda.play(); self.moedas.remove(m); self.jogador.pontos += 50
        for e in self.estrelas[:]:
            if self.jogador.rect.colliderect(e.rect):
                self.estrelas.remove(e); self.jogador.pontos += 100
        
        if self.jogador.rect.right >= largura - 10:
            return Victory(self.jogador)
        return None

    def draw(self, tela):
        tela.blit(self.fundo, (0,0))
        self.chao.desenhar(tela)
        for p in self.plataformas: p.desenhar(tela)
        for t in self.trampolins: t.desenhar(tela)
        for i in self.inimigos: i.desenhar(tela)
        for i2 in self.inimigos2: i2.desenhar(tela)
        for m in self.moedas: m.desenhar(tela)
        for e in self.estrelas: e.desenhar(tela)
        for es in self.estacas: es.desenhar(tela)
        self.jogador.desenhar(tela)


class Victory(Cena):
    def __init__(self, jogador):
        pygame.mixer.music.load('som/mscVitoria.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.jogador = jogador
        try:
            self.imagem = pygame.image.load("imagens/victory.png")
            self.imagem = pygame.transform.scale(self.imagem, (largura, altura))
        except pygame.error as e:
            print(f"Erro fatal ao carregar imagem inicial: {e}")
            self.imagem = pygame.Surface((largura, altura))
            self.imagem.fill((0,0,0))
            fonte_erro = pygame.font.Font(None, 50)
            texto_erro = fonte_erro.render("Erro: 'som/mscVitoria.mp3' nao encontrada.", True, (255, 0, 0))
            rect_erro = texto_erro.get_rect(center=(largura // 2, altura // 2))
            self.imagem.blit(texto_erro, rect_erro)

        self.botao_rect = pygame.Rect(750, 645, 400, 70)  # Continuar -> FinalScene
        self.botao_menu = pygame.Rect(750, 725, 400, 70)  # Novo: Menu -> CenaInicial
        self.botao_sair = pygame.Rect(largura - 250, 25, 250, 40)

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.botao_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return FinalScene(self.jogador)
                elif self.botao_menu.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return CenaInicial(self.jogador)
                elif self.botao_sair.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        return None

    def update(self):
        return None

    def draw(self, tela):
        tela.blit(self.imagem, (0, 0))
        # pygame.draw.rect(tela, (200, 200, 200), self.botao_rect, 2)
        # pygame.draw.rect(tela, (0, 200, 0), self.botao_menu, 2)
        # pygame.draw.rect(tela, (200, 0, 0), self.botao_sair, 2)

class VictorySubCena3(Cena):
    def __init__(self, jogador):
        pygame.mixer.music.load('som/mscVitoria.mp3')  # Se quiser uma música diferente
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.jogador = jogador
        try:
            self.imagem = pygame.image.load("imagens2/victory2.png")
            self.imagem = pygame.transform.scale(self.imagem, (largura, altura))
        except pygame.error as e:
            print(f"Erro ao carregar imagem de vitória: {e}")
            self.imagem = pygame.Surface((largura, altura))
            self.imagem.fill((0, 0, 0))
            fonte_erro = pygame.font.Font(None, 50)
            texto_erro = fonte_erro.render("Erro: imagem victory2.png não encontrada.", True, (255, 0, 0))
            rect_erro = texto_erro.get_rect(center=(largura // 2, altura // 2))
            self.imagem.blit(texto_erro, rect_erro)

        self.botao_sair = pygame.Rect(710, 640, 400, 70)
        #self.botao_sair = pygame.Rect(largura - 250, 25, 250, 40)

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.botao_sair.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit()
              
        return None

    def update(self):
        return None

    def draw(self, tela):
        tela.blit(self.imagem, (0, 0))


class GameOver(Cena):
    def __init__(self, jogador_atual, cena_origem_classe):
        pygame.mixer.music.load('som/mscgameover.mp3')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

        self.jogador_atual = jogador_atual
        self.cena_origem_classe = cena_origem_classe

        self.botao_rect = pygame.Rect(750, 645, 400, 70)  # Tentar Novamente
        self.botao_rect2 = pygame.Rect(750, 725, 400, 70) # Menu Principal
        self.botao_sair = pygame.Rect(largura - 250, 25, 250, 40)
        self.imagem = self._carregar_imagem_gameover()

    def _carregar_imagem_gameover(self):
        cena_nome = self.cena_origem_classe.__name__
        caminho_imagem = "imagens/gameover1.png" # Padrão
        if cena_nome in ['SubCena1', 'SubCena2', 'SubCena3']:
            caminho_imagem = "imagens2/gameover2.png"
        
        try:
            imagem = pygame.image.load(caminho_imagem)
        except pygame.error as e:
            print(f"Erro ao carregar imagem gameover ({caminho_imagem}): {e}")
            # Fallback para uma surface simples se a imagem específica falhar
            try:
                imagem = pygame.image.load("imagens/gameover1.png") # Tenta o padrão se o específico falhar
            except pygame.error: # Se o padrão também falhar
                imagem = pygame.Surface((largura, altura)); imagem.fill((20,20,20))
                fonte = pygame.font.Font(None, 100); texto = fonte.render("GAME OVER", True, (255,0,0))
                rect = texto.get_rect(center=(largura//2, altura//2 - 50))
                imagem.blit(texto, rect)
        return pygame.transform.scale(imagem, (largura, altura))

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.botao_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()  #  Para a música da tela inicial
                    return self._get_restart_scene()
                elif self.botao_rect2.collidepoint(event.pos):
                    GameState.resetar_vidas() # Vidas resetadas ao ir pro menu
                    self.jogador_atual.vivo = True # Garante que o jogador esteja vivo
                    # self.jogador_atual.pontos = 0 # Opcional: zerar pontos
                    return CenaInicial(self.jogador_atual)
                elif self.botao_sair.collidepoint(event.pos):
                    pygame.quit(); sys.exit()
        return None

    def _get_restart_scene(self):
        GameState.resetar_vidas()
        self.jogador_atual.vivo = True
        # self.jogador_atual.pontos = 0 # Opcional: zerar pontos ao tentar a fase novamente
        print(f"DEBUG: Reiniciando para {self.cena_origem_classe.__name__}")
        return self.cena_origem_classe(self.jogador_atual)

    def draw(self, tela):
        tela.blit(self.imagem, (0, 0))
        # Opcional: Desenhar retângulos para debug dos botões
        # pygame.draw.rect(tela, (255,0,0), self.botao_rect, 2)
        # pygame.draw.rect(tela, (0,255,0), self.botao_rect2, 2)
        # pygame.draw.rect(tela, (0,0,255), self.botao_sair, 2)

class FinalScene(Cena):
    def __init__(self, jogador):
        self.jogador = jogador
        try:
            self.imagem = pygame.image.load("imagens2/NovoNivel.png")
            self.imagem = pygame.transform.scale(self.imagem, (largura, altura))
        except pygame.error as e:
            print(f"Erro ao carregar imagem FinalScene: {e}")
            self.imagem = pygame.Surface((largura, altura)); self.imagem.fill((50, 50, 100))
            fonte = pygame.font.Font(None, 70); texto = fonte.render("Nível Concluído!", True, (255,255,255))
            rect = texto.get_rect(center=(largura//2, altura//2 - 50))
            self.imagem.blit(texto, rect)

        self.botao_continuar = pygame.Rect(710, 550, 400, 70)
        self.botao_menu = pygame.Rect(710, 640, 400, 70)
        self.botao_sair = pygame.Rect(largura - 250, 25, 250, 40)

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.botao_continuar.collidepoint(event.pos):
                    GameState.resetar_vidas()  # ✅ Resetar vidas
                    self.jogador.vivo = True   # ✅ Garantir que está vivo
                    return SubCena1(self.jogador)

                elif self.botao_menu.collidepoint(event.pos):
                    # GameState.resetar_vidas() # Opcional aqui, pode ser que o jogador queira continuar com as vidas que tem
                    self.jogador.vivo = True
                    return CenaInicial(self.jogador) # Passa o jogador
                elif self.botao_sair.collidepoint(event.pos):
                    pygame.quit(); sys.exit()
        return None

    def update(self):
        return None

    def draw(self, tela):
        tela.blit(self.imagem, (0, 0))
        # Opcional: debug de botões
        # pygame.draw.rect(tela, (255, 255, 255), self.botao_continuar, 2)
        # pygame.draw.rect(tela, (255, 255, 255), self.botao_menu, 2)
        # pygame.draw.rect(tela, (255, 255, 255), self.botao_sair, 2)

class SubCena1(Cena):
    def __init__(self, jogador_existente):
        self.jogador = jogador_existente
        self.jogador.rect.topleft = (50, 710) # Posição inicial na SubCena1
        self.jogador.vel_y = 0
        self.jogador.no_chao = False

        try:
            self.fundo = pygame.image.load('imagens2/SubCena1.png')
            self.fundo = pygame.transform.scale(self.fundo, [largura, altura])
            self.coracao_img = pygame.image.load('imagens/coracao.png').convert_alpha()
            self.coracao_img = pygame.transform.scale(self.coracao_img, (75, 75))
        except pygame.error as e:
            print(f"Erro ao carregar imagens para SubCena1: {e}")
            self.fundo = pygame.Surface((largura, altura)); self.fundo.fill((50,150,50))
            self.coracao_img = pygame.Surface((75,75)); self.coracao_img.fill((255,0,0))

        self.chao = Chao() # O chão "real" está coberto por fogo, mas a classe é usada para colisões
        self.plataformas = [
    
            # Esquerda
            Plataforma(4, 800),
            Plataforma(80, 800),
            Plataforma(167, 800),
            Plataforma(250, 800),  #baixo 1
            Plataforma(339, 800),
            Plataforma(428, 800),
            Plataforma(517, 800),

            Plataforma(5, 710),
            Plataforma(90, 710), #cima2
            Plataforma(175, 710),

            Plataforma(1050, 620),
            Plataforma(880, 710), #lado
            Plataforma(965, 710),
            Plataforma(1050, 710),

            Plataforma(293, 430),
            Plataforma(382, 430), #na escada
            Plataforma(470, 430),
            Plataforma(558, 430),

            Plataforma(700, 280),
            Plataforma(785, 280),
            Plataforma(870, 280),

            Plataforma(1300, 150),
            Plataforma(1378, 150), #cima direita
            Plataforma(1465, 150), #cima direita menos <- / -> mais
            Plataforma(1550, 150), #cima direita
            Plataforma(1210, 220),

            #Plataforma(1360, 570), #cima direita maior numero baixo, menor numero cima
            Plataforma(1360, 570), #cima direita maior numero baixo, menor numero cima

        ]
        self.moedas = gerar_moedas_sobre_plataformas(6, self.plataformas)
        self.estrelas = gerar_estrelas_sobre_plataformas(3, self.plataformas)
 
        self.inimigos = [
            Inimigo3(400, 700),  
        ]
        #self.moedas = [Moeda(600, 750), Moeda(1000, 550)]
        #self.estrelas = [Estrela(1300, 700)] # Posição original, verificar se alcançável
        self.fogos = [
            Fogo(50, 905,1500 , 130),  # Fogo no chão (x, y, largura, altura) # Fogo sobre o chão
        ]
        self.inimigos = [Inimigo(500, 430 - 70)] # Em cima da plataforma
        self.inimigos3 = [Inimigo3(500, 800 - 80)] # Em cima da plataforma inicial
        self.trampolins = [Trampolim(50, 710 - 45)] # No início, em cima da plataforma

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
        return None

    def update(self):
        teclas = pygame.key.get_pressed()
        self.jogador.mover(teclas)
        self.jogador.aplicar_gravidade()
        self.jogador.checar_colisoes(
            plataformas=self.plataformas, chao=self.chao, trampolins=self.trampolins,
            inimigos=self.inimigos, inimigos3=self.inimigos3, fogos=self.fogos
        )

        if not self.jogador.vivo:
            return GameOver(self.jogador, SubCena1)

        for i in self.inimigos: i.update(self.plataformas, self.chao)
        for i3 in self.inimigos3: i3.update(self.plataformas)
        for f in self.fogos: f.update()

        for m in self.moedas[:]:
            if self.jogador.rect.colliderect(m.rect): som_moeda.play(); self.moedas.remove(m); self.jogador.pontos += 50
        for e in self.estrelas[:]:
            if self.jogador.rect.colliderect(e.rect): self.estrelas.remove(e); self.jogador.pontos += 100

        if self.jogador.rect.right >= largura - 50: # Condição de saída
            return SubCena2(self.jogador)
        return None

    def draw(self, tela):
        tela.blit(self.fundo, (0,0))
        self.chao.desenhar(tela) # Invisível, mas usado para lógica
        for p in self.plataformas: p.desenhar(tela)
        for f in self.fogos: f.desenhar(tela)
        for t in self.trampolins: t.desenhar(tela)
        for i in self.inimigos: i.desenhar(tela)
        for i3 in self.inimigos3: i3.desenhar(tela)
        for m in self.moedas: m.desenhar(tela)
        for e in self.estrelas: e.desenhar(tela)
        self.jogador.desenhar(tela)

class SubCena2(Cena):
    def __init__(self, jogador_existente):
        self.jogador = jogador_existente
        self.jogador.rect.topleft = (50, 800) # Posição inicial
        self.jogador.vel_y = 0
        self.jogador.no_chao = False
        
        try:
            self.fundo = pygame.image.load('imagens2/subcena2.png')
            self.fundo = pygame.transform.scale(self.fundo, [largura, altura])
            self.coracao_img = pygame.image.load('imagens/coracao.png').convert_alpha()
            self.coracao_img = pygame.transform.scale(self.coracao_img, (75, 75))
        except pygame.error as e:
            print(f"Erro ao carregar imagens para SubCena2: {e}")
            self.fundo = pygame.Surface((largura, altura)); self.fundo.fill((150,50,50))
            self.coracao_img = pygame.Surface((75,75)); self.coracao_img.fill((255,0,0))

        self.chao = Chao()

        self.plataformas = [
            Plataforma(300, 800), #chao

            Plataforma(300, 400), #cima esquerda

            Plataforma(550, 700), 
            Plataforma(638, 700),#tres juntos
            Plataforma(638, 610), 

            Plataforma(650, 200),
            Plataforma(738, 200), #cima direita
           
           Plataforma(1000, 500), #chao direita
            Plataforma(1300, 200), #chao direita
            Plataforma(1599, 500), #cima direita
            Plataforma(1687, 500), #chao direita
            Plataforma(1770, 500), #chao direita
            Plataforma(1850, 500), #chao direita
            
        ]

        self.moedas = gerar_moedas_sobre_plataformas(6, self.plataformas)
        self.estrelas = gerar_estrelas_sobre_plataformas(3, self.plataformas)
        self.fogos = [
            Fogo(499, 905, 1191, 130),  # Fogo no chão (x, y, largura, altura) - Largura ajustada para não ficar sob plataforma final
           ]
        self.trampolins = [
            #Trampolim(300, 800 - 45), # Em cima da plataforma do chão
            Trampolim(1020, 460, 45),
        ] # Em cima das plataformas
    

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
        return None

    def update(self):
        teclas = pygame.key.get_pressed()
        self.jogador.mover(teclas)
        self.jogador.aplicar_gravidade()
        # Adicionar listas vazias para outros tipos de objetos se checar_colisoes os esperar
        self.jogador.checar_colisoes(self.plataformas, self.chao, trampolins=self.trampolins, inimigos=[], inimigos2=[], inimigos3=[], inimigos4=[], fogos=self.fogos,estacas=[]) #fogos=self.fogos, estacas=[])
 

        if not self.jogador.vivo:
            return GameOver(self.jogador, SubCena2)

        for m in self.moedas[:]:
            if self.jogador.rect.colliderect(m.rect): som_moeda.play(); self.moedas.remove(m); self.jogador.pontos += 50
        for e in self.estrelas[:]:
            if self.jogador.rect.colliderect(e.rect): self.estrelas.remove(e); self.jogador.pontos += 100

        if self.jogador.rect.right >= 1800 and self.jogador.no_chao:
            return SubCena3(self.jogador)
        return None

    def draw(self, tela):
        tela.blit(self.fundo, (0,0))
        self.chao.desenhar(tela)
        for p in self.plataformas: p.desenhar(tela)
        for m in self.moedas: m.desenhar(tela)
        for e in self.estrelas: e.desenhar(tela)
        for f in self.fogos: f.desenhar(tela)
        for t in self.trampolins: t.desenhar(tela)
        self.jogador.desenhar(tela)

class SubCena3(Cena):
    def __init__(self, jogador_existente):
        self.jogador = jogador_existente
        self.jogador.rect.topleft = (50, 710) # Posição inicial
        self.jogador.vel_y = 0
        self.jogador.no_chao = False

        try:
            self.fundo = pygame.image.load('imagens2/SubNivel3.png')
            self.fundo = pygame.transform.scale(self.fundo, [largura, altura])
            self.coracao_img = pygame.image.load('imagens/coracao.png').convert_alpha()
            self.coracao_img = pygame.transform.scale(self.coracao_img, (75, 75))
        except pygame.error as e:
            print(f"Erro ao carregar imagens para SubCena3: {e}")
            self.fundo = pygame.Surface((largura, altura)); self.fundo.fill((50,50,150))
            self.coracao_img = pygame.Surface((75,75)); self.coracao_img.fill((255,0,0))

        self.chao = Chao()
        self.plataformas = [
            
            Plataforma(4, 800),
            Plataforma(80, 800),
            Plataforma(167, 800),
            Plataforma(250, 800),  #baixo 1
            Plataforma(339, 800),

            Plataforma(590, 470),
            Plataforma(678, 470), #cima esquerda
            Plataforma(765, 470), #cima esquerda
            Plataforma(850, 470), #cima esquerda
            Plataforma(900, 470), #cima direita

            Plataforma(1150, 270), #chao direita
            Plataforma(1238, 270), #cima direita

            Plataforma(1500, 460), #cima direita

            Plataforma(1600, 750), #cima direita
            Plataforma(1687, 750), #cima direita
            Plataforma(1770, 750), #cima direita
            Plataforma(1850, 750), #cima direita
        ]
        self.moedas = gerar_moedas_sobre_plataformas(6, self.plataformas)
        self.estrelas = gerar_estrelas_sobre_plataformas(3, self.plataformas)
        self.fogos = [
            Fogo(180, 905, 1600, 130),  # Fogo no chão (x, y, largura, altura)
            
        ]
        self.inimigos4 = [
        #Inimigo4(500, 600), 
        #Inimigo4(800, 500),
]

        self.trampolins = [Trampolim(300, 800 - 45)] # No início, em cima da plataforma

    def handle_events(self, eventos):
        for event in eventos:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
        return None

    def update(self):
        teclas = pygame.key.get_pressed()
        self.jogador.mover(teclas)
        self.jogador.aplicar_gravidade()
        self.jogador.checar_colisoes(self.plataformas, self.chao, fogos=self.fogos, trampolins=self.trampolins, inimigos=[], inimigos2=[], inimigos3=[], inimigos4=[], estacas=[])


        if not self.jogador.vivo:
            return GameOver(self.jogador, SubCena3)
        
        for f in self.fogos: f.update()

        for i4 in self.inimigos4: i4.update()
           

        for m in self.moedas[:]:
            if self.jogador.rect.colliderect(m.rect): som_moeda.play(); self.moedas.remove(m); self.jogador.pontos += 50
        for e in self.estrelas[:]:
            if self.jogador.rect.colliderect(e.rect): self.estrelas.remove(e); self.jogador.pontos += 100

        if self.jogador.rect.right >= largura - 50:
            self.jogador.vivo = True
            return VictorySubCena3(self.jogador)

        return None
    

    def draw(self, tela):
        tela.blit(self.fundo, (0,0))
        self.chao.desenhar(tela)
        for p in self.plataformas: p.desenhar(tela)
        for f in self.fogos: f.desenhar(tela)
        for i4 in self.inimigos4:  i4.desenhar(tela)
        for m in self.moedas: m.desenhar(tela)
        for e in self.estrelas: e.desenhar(tela)
        for t in self.trampolins: t.desenhar(tela)
        self.jogador.desenhar(tela)

def main():
    jogador = Jogador()
    cena_atual = CenaInicial(jogador)

    while True:
        eventos = pygame.event.get()
        # Primeiro, processa eventos para a cena atual
        # Isso pode resultar em uma nova cena (ex: botão clicado)
        resultado_eventos = cena_atual.handle_events(eventos)
        if resultado_eventos: # Se handle_events retornou uma nova cena
            cena_atual = resultado_eventos
            # Reinicia o loop para processar eventos e update da nova cena no próximo frame
            # antes de desenhar, para evitar desenhar um estado intermediário.
            relogio.tick(FPS) # Mantém o FPS mesmo em transição
            continue 

        # Se não houve mudança de cena pelos eventos, atualiza a cena atual
        # Isso pode resultar em uma nova cena (ex: jogador morreu, passou de fase)
        resultado_update = cena_atual.update()
        if resultado_update: # Se update retornou uma nova cena
            cena_atual = resultado_update
            relogio.tick(FPS)
            continue

        # Se nenhuma transição ocorreu, desenha a cena atual
        cena_atual.draw(tela)
        pygame.display.flip()
        relogio.tick(FPS)

if __name__ == "__main__":
    main()
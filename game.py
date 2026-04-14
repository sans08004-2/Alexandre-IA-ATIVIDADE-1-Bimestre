import pygame
import random
import textwrap
import json
from groq import Groq

# --- Configuração ---
#  sua chave de API 
CHAVE_API_GROQ = "CHAVE API GROK"
cliente = Groq(api_key=CHAVE_API_GROQ)

LARGURA, ALTURA = 800, 600
BRANCO = (220, 220, 220)
CINZA = (40, 40, 40) 
AZUL_ESCURO = (20, 20, 60)
PRETO = (10, 10, 10)
FPS = 60
VELOCIDADE_BOLA = 5
VELOCIDADE_RAQUETE = 4 # IA começa levemente mais lenta que a bola

class JogoPong:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Pong Neural: IA Adaptativa")
        self.relogio = pygame.time.Clock()
        self.fonte_interface = pygame.font.SysFont("Courier", 18)
        self.fonte_fundo = pygame.font.SysFont("Courier", 22, bold=True)

        self.bola = pygame.Rect(LARGURA//2, ALTURA//2, 15, 15)
        self.jogador = pygame.Rect(50, ALTURA//2 - 50, 10, 100)
        self.oponente = pygame.Rect(LARGURA - 60, ALTURA//2 - 50, 10, 100)
        
        self.bola_dx = VELOCIDADE_BOLA
        self.bola_dy = VELOCIDADE_BOLA
        
        # Estado da Lógica da IA
        self.pontos_jogador = 0
        self.pontos_ia = 0
        self.nome_estrategia = "AGUARDANDO"
        self.pensamento_ia = "Esperando o início do jogo..."
        self.multiplicador_vel_ia = 1.0
        self.margem_erro = 0 

    def buscar_adaptacao_ia(self):
        """Solicita ao Groq uma nova estratégia após perder um ponto."""
        prompt = (
            f"SISTEMA: A IA perdeu um ponto. Placar: Jogador {self.pontos_jogador}, IA {self.pontos_ia}. "
            "Responda em JSON estrito com os campos: "
            '{"estrategia": "nome curto da estrategia", '
            '"monologo": "pensamento curto em português sobre por que falhou", '
            '"aumento_velocidade": 0.1 a 0.3}'
        )

        print("\n--- [DEBUG: CHAMADA DE API] ---")
        
        try:
            resposta_chat = cliente.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}
            )
            res_bruta = resposta_chat.choices[0].message.content
            print(f"--- [DEBUG: RESPOSTA DA IA] ---\n{res_bruta}")
            
            dados = json.loads(res_bruta)
            self.nome_estrategia = dados.get("estrategia", "RECUPERAÇÃO")
            self.pensamento_ia = dados.get("monologue", "Preciso me adaptar.")
            self.multiplicador_vel_ia += dados.get("aumento_velocidade", 0.1)
            
            # IA tenta compensar o erro após aprender
            self.margem_erro = random.randint(-40, 40)

        except Exception as e:
            print(f"ERRO DE API: {e}")
            self.pensamento_ia = "ERRO DE CONEXÃO: OPERANDO EM MODO DE EMERGÊNCIA."

    def mover_ia(self):
        """Lógica de movimento com imperfeições para permitir derrotas."""
        if self.bola_dx > 0: # Só rastreia se a bola estiver vindo
            alvo_y = self.bola.y + self.margem_erro
            if self.oponente.centery < alvo_y:
                self.oponente.y += VELOCIDADE_RAQUETE * self.multiplicador_vel_ia
            elif self.oponente.centery > alvo_y:
                self.oponente.y -= VELOCIDADE_RAQUETE * self.multiplicador_vel_ia

    def resetar_bola(self, vencedor):
        if vencedor == "jogador":
            self.buscar_adaptacao_ia()
        else:
            self.margem_erro = random.randint(-60, 60)
            print("IA Marcou: Recalibrando margem de erro...")

        self.bola.center = (LARGURA//2, ALTURA//2)
        self.bola_dx = -VELOCIDADE_BOLA if vencedor == "ia" else VELOCIDADE_BOLA
        self.bola_dy = random.choice([VELOCIDADE_BOLA, -VELOCIDADE_BOLA])
        pygame.time.delay(1000)

    def executar(self):
        rodando = True
        while rodando:
            self.tela.fill(PRETO)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT: rodando = False

            # Controles do Jogador
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_UP] and self.jogador.top > 0: self.jogador.y -= VELOCIDADE_RAQUETE + 1
            if teclas[pygame.K_DOWN] and self.jogador.bottom < ALTURA: self.jogador.y += VELOCIDADE_RAQUETE + 1

            self.mover_ia()

            # Movimento da Bola
            self.bola.x += self.bola_dx
            self.bola.y += self.bola_dy

            if self.bola.top <= 0 or self.bola.bottom >= ALTURA: self.bola_dy *= -1
            
            # Colisões
            if self.bola.colliderect(self.jogador) and self.bola_dx < 0:
                self.bola_dx *= -1
                self.margem_erro = random.randint(-50, 50)
            if self.bola.colliderect(self.oponente) and self.bola_dx > 0:
                self.bola_dx *= -1

            # Pontuação
            if self.bola.left <= 0:
                self.pontos_ia += 1
                self.resetar_bola("ia")
            if self.bola.right >= LARGURA:
                self.pontos_jogador += 1
                self.resetar_bola("jogador")

            # Renderização
            self.desenhar_interface_fundo()
            pygame.draw.rect(self.tela, BRANCO, self.jogador)
            pygame.draw.rect(self.tela, BRANCO, self.oponente)
            pygame.draw.ellipse(self.tela, BRANCO, self.bola)
            pygame.display.flip()
            self.relogio.tick(FPS)

    def desenhar_interface_fundo(self):
        texto_estrategia = self.fonte_fundo.render(f"ESTRATÉGIA: {self.nome_estrategia.upper()}", True, AZUL_ESCURO)
        self.tela.blit(texto_estrategia, (LARGURA//2 - texto_estrategia.get_width()//2, 100))
        
        linhas = textwrap.wrap(self.pensamento_ia, width=40)
        for i, linha in enumerate(linhas):
            surf_linha = self.fonte_fundo.render(linha, True, CINZA)
            self.tela.blit(surf_linha, (LARGURA//2 - surf_linha.get_width()//2, ALTURA//2 + (i * 25)))

if __name__ == "__main__":
    JogoPong().executar()
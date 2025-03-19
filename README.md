# ♟️ Chess-IA

Chess-IA es una actividad escolar con la finalidad de poner a dos modelos de ajedrez a jugar una partida.

## ⌨  Lenguaje utilizado:
### 🐍Python

#### 🤔 ¿Qué es? 
Python es un lenguaje de alto nivel de programación interpretado cuya filosofía hace hincapié en la legibilidad de su código. Se trata de un lenguaje de programación multiparadigma, ya que soporta parcialmente la oriantación a objetos, programación imperativa y, en menor medida, programación funcional. Es un lenguaje interpretado, dinámico y multiplataforma.

Administrado por Python Software Foundation, posee una licencia de código abierto, denominada Python Software Foundation License. Python se clasifica constantemente como una de los lenguajes de programación más populares.

#### 🤨 ¿Por qué se utilizó? 
Python es un lenguaje de programación fácil de entender para un recién iniciado en el código. Además, cuenta con demasiadas librerías que resuelven muchas problemáticas.

Se utilizó Python 3.12.7, con PyCharm como IDE, desde Ubuntu, Linux.

### 🕮  Librerías utilizadas
Las librerías de ajedrez utilizadas están específicadas en el archivo "requirements.txt". Estas librerías se escogieron por las herramientas que brindan, tanto las reglas del ajedrez, como la visualización del tablero y movimiento. Las librerías completas son las siguientes:

<pre><code>
	import chess
	import subprocess
	import time
	import os
	import sys
	import pygame
	import threading 
</code></pre>

## 🖥️  Modelos Utilizados:
Un módulo de ajedrez es un programa de ordenador que analzia posiciones de ajedrez, y transmite lo que calcula y considera son las mejores jugadas a disposición. Si los ordenadores fueran jugadores de ajedrez, los módulos serían sus cerebros.

Los módulos de ajedrez son mucho más fuertes que los seres humanos, y los mejores módulos alcanzan un ELO de más de 3000 puntos. Asimismo, los módulos se vuelven más y más fuertes con cada año que pasa gracias a las mejoras y avances en hardware y software.

### ♔ Stockfish
En la actualidad, Stockfish es el módulo de ajedrez más fuerte que está disponible para el público. Al ser un módulo de código abierto, toda una comunidad de personas está ayudando a desarrollarlo y mejorarlo. Al igual que muchos otros, Stockfish ha incluido redes neuronales en su código para mejorar aún más la evaluación de posiciones de ajedrez.

Stockfish está disponible al público en todas las principales plataformas como Windows, Mac OS X, Linux iOS, y Android.
### ♕ Crafty
Crafty es un programa de ajedrez escrito por Robert Hyatt, profesor de la Universidad de Alabama en Birmigham. El programa es una derivación de Cray Blitz, ganador del Campeonato Mundial de Programas de Ajedrez (WCCC) de 1983 y de 1986. En febrero del año 2006, Craft aparecía en las listas de clasificación SSDF en la posición 36, con un ELO de 2657.

El código abierto de Crafty está escrito en ANSI C, y por tanto es muy versátil. Sin embargo, el crecimiento del rendimiento de algunas CPU hace posible que se puedan usar otros lenguajes de programación que dará como resulatado un incremento del rendimiento. El código está disponible gratis, por lo que ha sido copiado por varios grandes programas de Ajedrez de elite.



## 📋 Referencias

- [Lenguaje de programación Python](https://es.wikipedia.org/wiki/Python)
- [Módulos de programación](https://www.chess.com/es/terms/modulos-de-ajedrez)
- [Crafty](https://es.wikipedia.org/wiki/Crafty)

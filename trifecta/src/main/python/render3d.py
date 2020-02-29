import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def render_line(*verticies):
    glBegin(GL_LINES)

    glVertex3fv(verticies[0])
    for vertex in verticies[1:-1]:
        for i in range(2):
            glVertex3fv(vertex)
    glVertex3fv(verticies[-1])

    glEnd()

def render_body(head:tuple, neck:tuple, left_shoudler:tuple, left_elbow:tuple, left_hand:tuple, right_shoudler:tuple, right_elbow:tuple, right_hand:tuple):
    # torso
    render_line(head, neck)
    # left
    render_line(neck, left_shoudler, left_elbow, left_hand)
    # right
    render_line(neck, right_shoudler, right_elbow, right_hand)

def rotate_screen(mouse_info, fps):
    mouse1 = mouse_info.get_pressed()[0]
    delta_x, delta_y = mouse_info.get_rel()
    c = 10
    if (mouse1):
        glRotate(delta_x / fps * c, 0, 1, 0)
        glRotate(delta_y / fps * c, 1, 0, 0)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    clock = pygame.time.Clock()
    gluPerspective(45, display[0]/display[1], 0.1, 50.0)
    glTranslate(0.0, 0.0, -5);
    glRotate(0, 0, 0, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        clock.tick()
        rotate_screen(pygame.mouse, clock.get_fps())
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        render_body((0, 1, 0), (0, 0, 0), (1, 0, 0), (1.5, -1, 0), (1, -2, 0), (-1, 0, 0), (-1.5, -1, 0), (-1, -2, 0))
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == '__main__':
    main()

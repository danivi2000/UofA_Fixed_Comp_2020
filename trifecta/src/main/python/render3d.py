import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math


def render_line(*verticies):
    glBegin(GL_LINES)

    glVertex3fv(verticies[0])
    for vertex in verticies[1:-1]:
        for i in range(2):
            glVertex3fv(vertex)
    glVertex3fv(verticies[-1])

    glEnd()


def render_sphere(vertex:tuple, radius:float, slices:int, stack:int):
    for i in range(slices + 1):
        angle_i = i * math.tau / slices
        s = []
        for j in range(stack + 1):
            angle_j = j * math.pi / stack
            s.append((vertex[0] + math.sin(angle_i) * math.sin(angle_j) * radius,
                    vertex[1] + math.cos(angle_j) * radius, vertex[2]
                    + math.cos(angle_i) * math.sin(angle_j) * radius))
        render_line(*s)

    for j in range(stack + 1):
        angle_j = j * math.pi / stack
        s = []
        for i in range(slices + 1):
            angle_i = i * math.tau / slices
            s.append((vertex[0] + math.sin(angle_i) * math.sin(angle_j) * radius,
                vertex[1] + math.cos(angle_j) * radius, vertex[2]
                + math.cos(angle_i) * math.sin(angle_j) * radius))
        render_line(*s)


def render_axis():
    glColor3b(90, 90, 90)
    render_line((0, 0, 0), (5, 0, 0))
    render_line((0, 0, 0), (0, 5, 0))
    render_line((0, 0, 0), (0, 0, 5))


def render_body(
    head:tuple, neck:tuple,
    left_shoudler:tuple, left_elbow:tuple,left_hand:tuple,
    right_shoudler:tuple, right_elbow:tuple, right_hand:tuple
):
    glColor3b(0, 100, 0)
    # torso
    render_line(head, neck)
    render_sphere(head, 0.5, 8, 8)
    # left
    render_line(neck, left_shoudler, left_elbow, left_hand)
    # right
    render_line(neck, right_shoudler, right_elbow, right_hand)


def rotate_screen(mouse_info, fps):
    mouse1, mouse3, mouse2 = mouse_info.get_pressed()
    delta_x, delta_y = mouse_info.get_rel()
    r = 10
    t = 0.4
    if (mouse1):
        glRotate(delta_x / fps * r, 0, 1, 0)
        glRotate(delta_y / fps * r, 1, 0, 0)
    if (mouse2):
        glTranslate(delta_x / fps * t, 0, 0)
        glTranslate(0, -delta_y / fps * t, 0)


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    clock = pygame.time.Clock()
    gluPerspective(45, display[0]/display[1], 0.1, 50.0)
    glTranslate(0, 0, -5);
    glRotate(45, 0, 1, 0)
    glRotate(45, 1, 0, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        clock.tick()
        rotate_screen(pygame.mouse, clock.get_fps())
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        render_axis()
        render_body(
            (0, 1, 0), (0, 0, 0),
            (1, 0, 0), (1.5, -1, 0), (1, -2, 0),
            (-1, 0, 0), (-1.5, -1, 0), (-1, -2, 0)
        )
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == '__main__':
    main()

import pygame
import pymunk
import pymunk.pygame_util
import sys

pygame.init()

# ---- Настройки окна ----
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Sandbox Stable")
clock = pygame.time.Clock()

# ---- Физика ----
space = pymunk.Space()
space.gravity = (0, 500)
space.iterations = 25  # стабильность
draw_options = pymunk.pygame_util.DrawOptions(screen)

# ---- Стены ----
walls = [
    pymunk.Segment(space.static_body, (60, 150), (60, HEIGHT-50), 6),
    pymunk.Segment(space.static_body, (WIDTH-60, 150), (WIDTH-60, HEIGHT-50), 6),
    pymunk.Segment(space.static_body, (60, HEIGHT-50), (WIDTH-60, HEIGHT-50), 6),
]

for w in walls:
    w.elasticity = 0.4
    w.friction = 0.9

space.add(*walls)

# ---- Ограничение скорости ----
def limit_velocity(body, gravity, damping, dt):
    pymunk.Body.update_velocity(body, gravity, damping, dt)
    max_vel = 800
    if body.velocity.length > max_vel:
        body.velocity = body.velocity.normalized() * max_vel

# ---- Drag система ----
mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
drag_joint = None

# ---- Создание фигур ----
def create_shape(shape_type):
    mass = 1
    elasticity = 0.4
    friction = 0.8

    if shape_type == 1:  # Синий куб
        size = 40
        moment = pymunk.moment_for_box(mass, (size, size))
        body = pymunk.Body(mass, moment)
        shape = pymunk.Poly.create_box(body, (size, size))
        shape.color = (70,130,255,255)

    elif shape_type == 2:  # Зеленый шар
        radius = 20
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        shape = pymunk.Circle(body, radius)
        shape.color = (60,200,60,255)

    elif shape_type == 3:  # Розовый супер-отталкивающий шар
        radius = 22
        mass = 0.8  # легче для сильного отскока
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        shape = pymunk.Circle(body, radius)
        shape.color = (255,105,180,255)
        shape.elasticity = 1.5  # сильный отскок
        shape.friction = 0.3

    elif shape_type == 4:  # Жёлтый треугольник
        points = [(-20,20),(0,-20),(20,20)]
        moment = pymunk.moment_for_poly(mass, points)
        body = pymunk.Body(mass, moment)
        shape = pymunk.Poly(body, points)
        shape.color = (240,200,60,255)

    body.position = (WIDTH//2, 220)
    shape.friction = friction
    shape.elasticity = elasticity
    body.velocity_func = limit_velocity

    space.add(body, shape)
    return body

# ---- UI панели для выбора фигур ----
ui_shapes = [
    (1, pygame.Rect(50, 40, 40, 40)),
    (2, pygame.Rect(150, 40, 40, 40)),
    (3, pygame.Rect(250, 40, 40, 40)),
    (4, pygame.Rect(350, 40, 40, 40)),
]

def draw_ui():
    pygame.draw.rect(screen, (30,30,30), (0,0,WIDTH,120))
    # Куб синий
    pygame.draw.rect(screen, (70,130,255), ui_shapes[0][1])
    # Шар зеленый
    pygame.draw.circle(screen, (60,200,60), ui_shapes[1][1].center, 20)
    # Розовый шар с обводкой
    pygame.draw.circle(screen, (255,105,180), ui_shapes[2][1].center, 22)
    pygame.draw.circle(screen, (200,20,100), ui_shapes[2][1].center, 22, 3)
    # Жёлтый треугольник
    pygame.draw.polygon(screen, (240,200,60),
                        [(370,40),(350,80),(390,80)])

# ---- Основной цикл ----
running = True
while running:
    clock.tick(60)
    screen.fill((255,255,255))
    draw_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            # Берём с панели
            for shape_type, rect in ui_shapes:
                if rect.collidepoint(pos):
                    create_shape(shape_type)
                    break
            else:
                # Захват объекта
                hit = space.point_query_nearest(pos, 5, pymunk.ShapeFilter())
                if hit and hit.shape.body.body_type == pymunk.Body.DYNAMIC:
                    mouse_body.position = pos
                    drag_joint = pymunk.PivotJoint(
                        mouse_body,
                        hit.shape.body,
                        (0,0),
                        hit.shape.body.world_to_local(pos)
                    )
                    drag_joint.max_force = 7000
                    drag_joint.error_bias = (1 - 0.2) ** 60
                    space.add(drag_joint)

        if event.type == pygame.MOUSEBUTTONUP:
            if drag_joint:
                space.remove(drag_joint)
                drag_joint = None

    if drag_joint:
        mouse_body.position = pygame.mouse.get_pos()

    space.step(1/60)

    pygame.draw.rect(screen, (0,0,0), (60,150,WIDTH-120,HEIGHT-200), 2)
    space.debug_draw(draw_options)

    pygame.display.flip()

pygame.quit()
sys.exit()

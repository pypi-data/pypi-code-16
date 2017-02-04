def drawline(turt,a,b,c,d):
    turt.pu()
    turt.goto(a,b)
    turt.pendown()
    turt.goto(c,d)

def makegraph(turt):
    drawline(turt, -1000, 0, 1000, 0)
    drawline(turt, 0, -1000, 0, 1000)

def get_quad_values(quad_num, size, count):
    if quad_num == 1:
        return size, size*count
    elif quad_num == 2:
        return -size, size*count
    elif quad_num == 3:
        return -size, -(size*count)
    elif quad_num == 4:
        return size, -(size*count)

def draw_quad(turt, quad_num, size, count=10):
    x, y = get_quad_values(quad_num, size, count)
    for _ in range(count):
        drawline(turt, x, 0,0,y)
        if x < 0:
            x -= size
        else:
            x += size

        if y < 0:
            y += size
        else:
            y -= size

def draw_all_quads(turt, size, count=10):
    for i in range(1,5):
        draw_quad(turt, i, size, count)

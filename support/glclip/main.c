#include <ApplicationServices/ApplicationServices.h>

#include <OpenGL/OpenGL.h>
#include <GLUT/glut.h>

#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

int global_height = 1;
int global_width = 1;

#define viewrand(x) ((((double)random())/INT32_MAX)*(x))

void
display(void)
{
  int i,j;

  glDisable(GL_SCISSOR_TEST);
  glClearColor(0.1, 0.2, 0.3, 0);
  glClear(GL_COLOR_BUFFER_BIT);
  glEnable(GL_SCISSOR_TEST);

  glPushMatrix();

  glEnableClientState(GL_VERTEX_ARRAY);
  srandom(((long)time(NULL))%INT32_MAX);
  for (i = 0; i < 100; i++) {
    double x1 = viewrand(global_width);
    double x2 = viewrand(global_width);
    double y1 = viewrand(global_height);
    double y2 = viewrand(global_height);
    double list[2][2] = {{x1, y1}, {x2, y2}};

    glVertexPointer(2, GL_DOUBLE, 0, (double *)list);
    glDrawArrays(GL_LINE_STRIP, 0, 2);
  }
  glDisableClientState(GL_VERTEX_ARRAY);

  glPopMatrix();

  glutSwapBuffers();
}

void
reshape(int width, int height)
{
  glLoadIdentity();
  glOrtho(0, width, height, 0, -1, 1);
  glViewport(0, 0, width, height);

  global_height = height;
  global_width  = width;

  double clip_x1 = ((double)width)*0.1;
  double clip_x2 = ((double)width)*0.9;
  double clip_y1 = ((double)height)*0.1;
  double clip_y2 = ((double)height)*0.9;

  glScissor(clip_x1, clip_y1, clip_x2 - clip_x1, clip_y2 - clip_y1);
}

int
main(int argc, char ** argv)
{
  glutInit(&argc, argv);
  glutInitDisplayMode(GLUT_RGBA|GLUT_DOUBLE);
  glutInitWindowSize(800, 600);
  glutCreateWindow("Clipping Test");

  glutDisplayFunc        (&display);
  glutReshapeFunc        (&reshape);

  //glutFullScreen();

  //glEnable(GL_CLIP_PLANE0);
  //glEnable(GL_CLIP_PLANE1);
  //glEnable(GL_CLIP_PLANE2);
  //glEnable(GL_CLIP_PLANE3);
  glEnable(GL_SCISSOR_TEST);

  glEnable(GL_LINE_SMOOTH);
  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

  glutMainLoop();
}

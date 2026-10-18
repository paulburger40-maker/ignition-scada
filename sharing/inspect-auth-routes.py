from org.objectweb.asm import ClassReader,ClassVisitor,MethodVisitor,Opcodes
from java.lang import ClassLoader
class V(MethodVisitor):
 def __init__(self): MethodVisitor.__init__(self,Opcodes.ASM9)
 def visitMethodInsn(self,opcode,owner,name,desc,isInterface): print('call '+owner+'.'+name+' '+desc)
 def visitLdcInsn(self,c): print('constant '+str(c))
 def visitIntInsn(self,opcode,operand): print('integer '+str(operand))
 def visitJumpInsn(self,opcode,label): print('branch '+str(opcode))
class C(ClassVisitor):
 def __init__(self): ClassVisitor.__init__(self,Opcodes.ASM9)
 def visitMethod(self,access,name,desc,signature,exceptions):
  if name in ('handleSameSite','handleCrossSite','handle','matchesAuthRequest','matchesMobileRedirect'):
   print('METHOD '+name+' '+desc); return V()
for name in ['com/inductiveautomation/ignition/gateway/auth/route/CrossSiteRouteHandler','com/inductiveautomation/ignition/gateway/auth/federation/FederationRoutes']:
 print('CLASS '+name)
 reader=ClassReader(ClassLoader.getSystemResourceAsStream(name+'.class'));reader.accept(C(),ClassReader.SKIP_DEBUG)

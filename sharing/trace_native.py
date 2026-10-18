import sys
from java.lang import ClassLoader, System
from java.io import PrintWriter
from jdk.internal.org.objectweb.asm import ClassReader
from jdk.internal.org.objectweb.asm.util import TraceClassVisitor
name=sys.argv[1]
reader=ClassReader(ClassLoader.getSystemResourceAsStream(name.replace('.','/')+'.class'))
reader.accept(TraceClassVisitor(PrintWriter(System.out)),0)

from com.inductiveautomation.ignition.common.script import ScriptConfig
from java.lang import ClassLoader,System
from java.io import PrintWriter
from jdk.internal.org.objectweb.asm import ClassReader
from jdk.internal.org.objectweb.asm.util import TraceClassVisitor
reader=ClassReader(ClassLoader.getSystemResourceAsStream('com/inductiveautomation/ignition/common/script/ScriptConfig$StartupScript.class'))
reader.accept(TraceClassVisitor(PrintWriter(System.out)),0)

# Room and Compose ship consumer rules. Keep serialization companions for explicit generic command receipts.
-keepattributes Signature,InnerClasses,EnclosingMethod,RuntimeVisibleAnnotations,AnnotationDefault
-if @kotlinx.serialization.Serializable class **
-keepclassmembers class <1> { static <1>$Companion Companion; }
-keep,includedescriptorclasses class cn.datebook.core.**$$serializer { *; }
-dontwarn javax.annotation.**

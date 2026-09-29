package org.worldmedals.atlas;
final class UpdateVersion {
 static boolean valid(String tag){return tag!=null&&tag.matches("mobile-v[0-9]{1,6}\\.[0-9]{3}");}
 static long value(String version){String v=version.replaceFirst("^mobile-v", "");if(!v.matches("[0-9]{1,6}\\.[0-9]{3}"))throw new IllegalArgumentException("Invalid version");String[] parts=v.split("\\.");return Long.parseLong(parts[0])*1000+Long.parseLong(parts[1]);}
 static boolean newer(String remote,String local){return value(remote)>value(local);}
}

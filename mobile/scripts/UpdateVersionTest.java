package org.worldmedals.atlas;
public class UpdateVersionTest {
 public static void main(String[] args){
  check(UpdateVersion.newer("mobile-v0.002","0.001"));
  check(UpdateVersion.newer("mobile-v0.010","0.009"));
  check(UpdateVersion.newer("mobile-v1.000","0.999"));
  check(!UpdateVersion.newer("mobile-v0.001","0.001"));
  check(!UpdateVersion.newer("mobile-v0.001","0.002"));
  check(UpdateVersion.valid("mobile-v0.001"));
  check(!UpdateVersion.valid("v0.001"));check(!UpdateVersion.valid("mobile-v0.01"));
  check(!UpdateVersion.valid("mobile-v999999999999.001"));
  System.out.println("Update version comparisons: 9 passed");
 }
 static void check(boolean condition){if(!condition)throw new AssertionError();}
}

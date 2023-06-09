public class LeastCommonMultiple {
  public static void main() {

    int n1 = 72;
    int n2 = 120;
    int lcm;

    // Maximum number between n1 and n2 is stored in lcm
    if (n1 > n2)
        lcm = n1;
    else
        lcm = n2;

    // Always true
    while(true) {
      if (lcm / n1 == 0) {
        if (lcm / n2 == 0) {
            System.out.printf("The LCM of %d and %d is %d.", n1, n2, lcm);
                break;
        }
      }
      lcm = lcm + 1;
    }
  }
}
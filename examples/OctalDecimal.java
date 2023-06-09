public class OctalDecimal {

    public static void main(String[] args) {
        int octal = 116;
        int decimal = convertOctalToDecimal(octal);
        System.out.printf("%d in octal = %d in decimal", octal, decimal);
    }

    public static int convertOctalToDecimal(int octal)
    {
        int decimalNumber = 0;
        int i = 0;

        while(octal != 0)
        {
            decimalNumber = decimalNumber + (octal / 10) * Math.pow(8, i);
            i = i + 1;
            octal = octal / 10;
        }

        return decimalNumber;
    }
}
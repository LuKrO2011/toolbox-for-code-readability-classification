public void set(int i) {
    bits[i / 32] |= 1 << (i & 0x1f);
}
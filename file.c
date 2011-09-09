#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<fcntl.h>
#include<string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <curl/curl.h>
#include <curl/easy.h>

int main(int argc, char ** argv)
{
        int fd,amt=0,i,len,cmd_len=0;
        char data[4097];
        char *p,*q;
        char dest[4096]="\"http://localhost:5080";
        char cmd[4096];
        CURL *curl;
        CURLcode res;

        
        fd=open(argv[1],O_RDONLY);
        struct stat stb;
        fstat(fd, &stb);
        lseek(fd, 0, SEEK_SET);
        amt=stb.st_blksize;
        p=data;
        /* curl_easy_setopt(curl, CURLOPT_POSTFIELDS, "Shardul"); */
        /* curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, 7); */
        /* res = curl_easy_perform(curl); */
        

        for(i=0; i<stb.st_size; i+=stb.st_blksize)
        {
                if(i+amt > stb.st_size)
                        amt=stb.st_size - i;
                read(fd, p, amt);

                curl=curl_easy_init();
                curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:5080");
                curl_easy_setopt(curl, CURLOPT_POST, "Take Care");
                
                curl_easy_setopt(curl, CURLOPT_POSTFIELDS, p);
                curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, amt);
        
                res = curl_easy_perform(curl);
                curl_easy_cleanup(curl);                        
                
        }
}

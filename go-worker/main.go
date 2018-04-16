package main

import (
	"crypto/md5"
	"crypto/tls"
	"fmt"
	"log"
	"net"
	"os"
	"time"

	"gopkg.in/mgo.v2/bson"

	"gopkg.in/mgo.v2"
)

// State store the current state of a container group in the mongo database
// Current states include InProgress and Done
type State struct {
	Name  string `json:"name"`
	State string `json:"sate"`
}

func main() {

	work, ok := os.LookupEnv("MESSAGE")
	if !ok {
		log.Fatal("Env Variable MESSAGE Not Set.")
	}

	containerName, ok := os.LookupEnv("CONTAINER_NAME")
	if !ok {
		log.Fatal("Env Variable CONTAINER_NAME Not Set.")
	}

	//Make sure not not have the ssl=true param in the url
	mongoURI, ok := os.LookupEnv("DATABASE_URI")
	if !ok {
		log.Fatal("Env Variable DATABASE_URI Not Set.")
	}

	// Sanity checks
	log.Println("Processing work: ", work)
	log.Println("Container Name: ", containerName)

	dialInfo, err := mgo.ParseURL(mongoURI)
	if err != nil {
		log.Fatal(err)
	}

	dialInfo.DialServer = func(addr *mgo.ServerAddr) (net.Conn, error) {
		return tls.Dial("tcp", addr.String(), &tls.Config{})
	}

	session, err := mgo.DialWithInfo(dialInfo)
	if err != nil {
		log.Fatal(err)
	}
	defer session.Close()

	session.SetSafe(&mgo.Safe{})

	c := session.DB("containerstate").C("containerstate")

	log.Println("Adding Recored to Databases")

	//Record container started the work
	err = c.Insert(&State{
		Name:  containerName,
		State: "InProgress",
	})
	if err != nil {
		log.Fatal(err)
	}

	var states []State
	err = c.Find(bson.M{}).All(&states)
	if err != nil {
		log.Fatal(err)
	}

	//Perfom some hashing as work
	stop := make(chan bool)

	go func() {
		hash := md5.New()

		t := []byte("test")
		for {
			select {
			case <-stop:
				return
			default:
				time.Sleep(time.Second * 1)
				for i := 0; i < 20; i++ {
					t = hash.Sum(t)
					fmt.Printf("%x\n", t)
				}
			}
		}
	}()

	time.Sleep(time.Second * 5)
	stop <- true

	// Record finish work in the database
	c.Update(bson.M{"name": containerName}, bson.M{"$set": bson.M{"state": "Done"}})
}

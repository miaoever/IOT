
/******************************************************************************************************************
* File:REST.js
* Course: IOT, Data Science, Machine Learning
* Project: Fullfillment Center
* Copyright: Copyright (c) 2018 Carnegie Mellon University
* Versions:
*   1.0 April 2018 - Initial write of course order server demo (lattanze).
*
* Description: This module provides the restful webservices for the Server.js Node server. This module contains GET,
* POST, and DELETE services.  
*
* Parameters: 
*   router - this is the URL from the client
*   connection - this is the connection to the database
*   md5 - This is the md5 hashing/parser... included by convention, but not really used 
*
* Internal Methods: 
*   router.get("/"... - returns the system version information
*   router.get("/orders"... - returns a listing of everything in the ws_orderinfo database
*   router.get("/orders/:order_id"... - returns the data associated with order_id
*   router.post("/order?"... - adds the new customer data into the ws_orderinfo database
*
* External Dependencies: mysql
*
******************************************************************************************************************/

var mysql   = require("mysql");     //Database

function REST_ROUTER(router,connection) {
    var self = this;
    self.handleRoutes(router,connection);
}

// Here is where we define the routes. Essentially a route is a path taken through the code dependent upon the 
// contents of the URL

REST_ROUTER.prototype.handleRoutes= function(router,connection) {

    // GET with no specifier - returns system version information
    // req paramdter is the request object
    // res parameter is the response object

    router.get("/",function(req,res){
        res.json({"Message":"Orders Webservices Server Version 1.0"});
    });
    
    // GET for /pending specifier - returns all pending orders currently stored in the database
    // req paramdter is the request object
    // res parameter is the response object
  
    router.get("/pending",function(req,res){
        console.log("Getting all database entries..." );
        var query = "SELECT * FROM ?? WHERE ??=?";
        var table = ["orders", "pending", true];
        query = mysql.format(query,table);
        connection.query(query,function(err,rows){
            if(err) {
                res.json({"Error" : true, "Message" : "Error executing MySQL query"});
            } else {
                res.json({"Error" : false, "Message" : "Success", "Orders" : rows});
            }
        });
    });

    // GET for /pending/id specifier - returns the pending order for the provided order ID
    // req paramdter is the request object
    // res parameter is the response object
     
    router.get("/pending/:id",function(req,res){
        console.log("Getting order ID: ", req.params.id );
        var query = "SELECT * FROM ?? WHERE ??=? AND ??=?";
        var table = ["orders","id", req.params.id,"pending",true];
        query = mysql.format(query,table);
        connection.query(query,function(err,rows){
            if(err) {
                res.json({"Error" : true, "Message" : "Error executing MySQL query"});
            } else {
                res.json({"Error" : false, "Message" : "Success", "Users" : rows});
            }
        });
    });

    // GET for /pendingcustorders specifier - returns the order for the provided order ID
    // req paramdter is the request object
    // res parameter is the response object
     
    router.get("/pendingcustorders/:customer",function(req,res){
        console.log("Getting orders for: ", req.params.customer );
        var query = "SELECT * FROM ?? WHERE ??=? AND ??=?";
        var table = ["orders","customer",req.params.customer,"pending",true];
        query = mysql.format(query,table);
        connection.query(query,function(err,rows){
            if(err) {
                res.json({"Error" : true, "Message" : "Error executing MySQL query"});
            } else {
                res.json({"Error" : false, "Message" : "Success", "Users" : rows});
            }
        });
    });

    // GET for /filled specifier - returns all filled orders currently stored in the database
    // req paramdter is the request object
    // res parameter is the response object
  
    router.get("/filled",function(req,res){
        console.log("Getting all database entries..." );
        var query = "SELECT * FROM ?? WHERE ??=?";
        var table = ["orders", "pending", false];
        query = mysql.format(query,table);
        connection.query(query,function(err,rows){
            if(err) {
                res.json({"Error" : true, "Message" : "Error executing MySQL query"});
            } else {
                res.json({"Error" : false, "Message" : "Success", "Orders" : rows});
            }
        });
    });

    // GET for /filledcustorders specifier - returns the filled orders for the specified customer
    // req paramdter is the request object
    // res parameter is the response object
     
    router.get("/filledcustorders/:customer",function(req,res){
        console.log("Getting orders for: ", req.params.customer );
        var query = "SELECT * FROM ?? WHERE ??=? AND ??=?";
        var table = ["orders","customer",req.params.customer,"pending",false];
        query = mysql.format(query,table);
        connection.query(query,function(err,rows){
            if(err) {
                res.json({"Error" : true, "Message" : "Error executing MySQL query"});
            } else {
                res.json({"Error" : false, "Message" : "Success", "Users" : rows});
            }
        });
    });

    // POST for making a pending order as satisfied for the provided order ID
    // This moves the order specified by ID to the fulfilled table.
    // req paramdter is the request object
    // res parameter is the response object
     
    router.post("/markOrderFilled/:id",function(req,res){
        console.log("Marking fulfilled order ID: ", req.params.id);
        var query = "UPDATE ?? SET ??=?, ??=? WHERE ??=?"
        var table = ["orders", "pending", false, "filldate", new (Date), "id", req.params.id];
        query = mysql.format(query,table);
        connection.query(query,function(err,rows){
            if(err) {
                res.json({"Error" : true, "Message" : "Error executing MySQL query"});
            } else {
                res.json({"Error" : false, "Message" : "Order marked filled", "Users" : rows});
            }
        });
    });

    // POST for adding orders
    // req paramdter is the request object - note to get parameters (eg. stuff afer the '?') you must use req.body.param
    // res parameter is the response object 
  
    router.post("/neworder",function(req,res){
        console.log("Adding order::", req.body.customer,",",req.body.red,",",req.body.blue,",",req.body.green,",",req.body.yellow,",",req.body.black,",",req.body.white);
        var query = "INSERT INTO ??(??,??,??,??,??,??,??,??) VALUES (?,?,?,?,?,?,?,?)";
        var table = ["orders","customer","red","blue","green","yellow","black","white","pending",req.body.customer,req.body.red,req.body.blue,req.body.green,req.body.yellow,req.body.black,req.body.white,true];
        query = mysql.format(query,table);
        connection.query(query,function(err,rows){
            if(err) {
                res.json({"Error" : true, "Message" : "Error executing MySQL query"});
            } else {
                res.json({"Error" : false, "Message" : "User Added !"});
            }
        });
    });

    // DELETE for deleting a pending order as satisfied for the provided order ID
    // req paramdter is the request object
    // res parameter is the response object
     
    router.delete("/deleteOrder/:id",function(req,res){
        console.log("Deleting order ID: ", req.params.id);
        var query = "DELETE FROM ?? WHERE ??=?";
        var table = ["orders", "id", req.params.id];
        query = mysql.format(query,table);
        connection.query(query,function(err,rows){
            if(err) {
                res.json({"Error" : true, "Message" : "Error executing MySQL query"});
            } else {
                res.json({"Error" : false, "Message" : "Delete order OK", "Users" : rows});
            }
        });
    });


}

// The next line just makes this module available... think of it as a kind package statement in Java

module.exports = REST_ROUTER;
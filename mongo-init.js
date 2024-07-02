db.createUser(
  {
    user: "admin",
    pwd: "password123",
    roles: [ { role: "root", db: "admin" } ]
  }
);


import 'package:flutter/material.dart';

class Header extends StatefulWidget {
  const Header({super.key});

  @override
  HeaderState createState() => HeaderState();
}

class HeaderState extends State<Header> {

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        height: 200,
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.4),
              blurRadius: 4,
              offset: const Offset(0, 5)
            ),
          ],
        ),
        child: const Row(
          children: [
            Padding(
              padding: EdgeInsets.all(4.0),
              child: CircleAvatar(
                maxRadius: 70,
                backgroundImage: NetworkImage(
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Baby.jpg/640px-Baby.jpg"
                ),
              ),
            ),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "Statrick",
                    style: TextStyle(
                      color: Color(0xffc0c4d7),
                      fontSize: 35
                    ),
                  ),
                ],
              ),
            )
          ],
        ),
      )
    );
  }
}
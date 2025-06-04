import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:smart_babyfoon/Components/home_content.dart';
import '../Components/baby_cam.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  HomeScreenState createState() => HomeScreenState();
}

class HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const HomeContent(),
    const BabyCam()
  ];

  @override
  void initState() {
    super.initState();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: _screens[_currentIndex]
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const <BottomNavigationBarItem> [
          BottomNavigationBarItem(
            icon: FaIcon(
              FontAwesomeIcons.house,
              size: 30,
            ),
            label: 'Home'
          ),
          BottomNavigationBarItem(
            icon: FaIcon(
              FontAwesomeIcons.camera,
              size: 30,
            ),
            label: 'Baby Monitor',
          ),
        ],
        selectedItemColor: const Color(0xff6070ff),
        unselectedItemColor: const Color(0xffc0c4d7),
      ),
    );
  }
}
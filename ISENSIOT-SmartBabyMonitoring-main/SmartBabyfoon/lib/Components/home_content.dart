import 'package:flutter/material.dart';
import 'package:smart_babyfoon/Components/Widgets/data_cards.dart';

import '../Components/Widgets/header.dart';

class HomeContent extends StatelessWidget {
  const HomeContent({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Column(
        children: [
          SizedBox(
              height: 210,
              child: Header()
          ),
          SizedBox(
            height: 400,
            child: DataCards(),
          ),
        ],
      )
    );
  }
}
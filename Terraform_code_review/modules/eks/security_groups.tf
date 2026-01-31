resource "aws_security_group" "cluster_additional" {
  name        = "${var.cluster_name}-cluster-additional"
  description = "Additional security group for EKS cluster"
  vpc_id      = var.vpc_id
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.cluster_name}-cluster-additional-sg"
    }
  )
}

resource "aws_security_group_rule" "cluster_ingress_https" {
  description       = "Allow HTTPS access to cluster API"
  security_group_id = aws_security_group.cluster_additional.id
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group" "node_additional" {
  name        = "${var.cluster_name}-node-additional"
  description = "Additional security group for EKS nodes"
  vpc_id      = var.vpc_id
  
  ingress {
    description = "Allow all traffic from within VPC"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.cluster_name}-node-additional-sg"
    }
  )
}
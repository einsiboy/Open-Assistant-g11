import { Button, ButtonProps } from "@chakra-ui/react";

interface ReferencesButtonProps extends ButtonProps {
  onClick: () => void;  // Handler for fetching references
}

export const ReferencesButton = ({ children, onClick, ...props }: ButtonProps) => {
  return (
    <Button size="lg" variant="solid" onClick={onClick} {...props}>
      {children}
    </Button>
  );
};
